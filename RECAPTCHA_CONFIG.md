# Configuración de reCAPTCHA v3 para Panel de Administración

## Descripción
Se ha implementado Google reCAPTCHA v3 en el formulario de login del panel de administración para mejorar la seguridad y prevenir ataques de bots.

## Funcionalidades Implementadas

### 1. Verificación Invisible
- reCAPTCHA v3 funciona de forma invisible al usuario
- No requiere hacer clic en checkboxes
- Analiza el comportamiento del usuario y asigna una puntuación de confianza

### 2. Validación del Lado del Servidor
- Verificación de la respuesta del reCAPTCHA con los servidores de Google
- Puntuación mínima requerida: 0.5 (configurable)
- Manejo de errores robusto

### 3. Integración con Django
- Implementación directa sin dependencias externas problemáticas
- Manejo de errores integrado con el sistema de mensajes de Django

## Configuración para Producción

### Paso 1: Obtener Claves de reCAPTCHA
1. Visita [Google reCAPTCHA Admin Console](https://www.google.com/recaptcha/admin)
2. Crea un nuevo sitio con las siguientes configuraciones:
   - **Tipo**: reCAPTCHA v3
   - **Dominio**: tu-dominio.com
   - **Propietarios**: tu email

### Paso 2: Actualizar Configuración
En `megadominio/settings.py`, reemplaza las claves de prueba:

```python
# reCAPTCHA configuration
RECAPTCHA_PUBLIC_KEY = 'TU_CLAVE_PUBLICA_REAL'
RECAPTCHA_PRIVATE_KEY = 'TU_CLAVE_PRIVADA_REAL'
RECAPTCHA_REQUIRED_SCORE = 0.5  # Ajusta según necesites
```

### Paso 3: Actualizar Template
En `adminpanel/templates/adminpanel/login.html`, actualiza la clave pública:

```html
<!-- Google reCAPTCHA v3 -->
<script src="https://www.google.com/recaptcha/api.js?render=TU_CLAVE_PUBLICA_REAL"></script>
```

Y en el JavaScript:
```javascript
const RECAPTCHA_SITE_KEY = 'TU_CLAVE_PUBLICA_REAL';
```

## Claves de Prueba (Actuales)
- **Clave Pública**: `6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI`
- **Clave Privada**: `6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe`

⚠️ **IMPORTANTE**: Estas son claves de prueba de Google. SIEMPRE devuelven resultados exitosos y NO deben usarse en producción.

## Funcionamiento

### Flujo de Validación
1. Usuario llena el formulario de login
2. Al enviar, se ejecuta reCAPTCHA v3 en el navegador
3. Se obtiene un token de verificación
4. El token se envía junto con las credenciales al servidor
5. El servidor verifica el token con Google reCAPTCHA API
6. Si la verificación es exitosa (score >= 0.5), se procesan las credenciales
7. Si falla, se muestra un mensaje de error

### Archivos Modificados
- `adminpanel/views.py`: Función `verify_recaptcha()` y lógica de validación
- `adminpanel/templates/adminpanel/login.html`: Script de reCAPTCHA y JavaScript
- `megadominio/settings.py`: Configuración de claves

## Personalización

### Ajustar Puntuación Mínima
Para cambiar el nivel de seguridad, modifica `RECAPTCHA_REQUIRED_SCORE` en settings.py:
- **0.0-0.3**: Muy probable que sea un bot
- **0.4-0.6**: Sospechoso
- **0.7-1.0**: Muy probable que sea humano

### Personalizar Mensajes
Los mensajes de error se pueden personalizar en `adminpanel/views.py`:
```python
messages.error(request, 'Tu mensaje personalizado aquí')
```

## Resolución de Problemas

### Error: "Por favor, completa la verificación de seguridad"
- Verifica que las claves sean correctas
- Asegúrate de que el dominio esté registrado en Google reCAPTCHA
- Revisa la consola del navegador para errores de JavaScript

### Error de Conexión
- Verifica la conexión a internet
- Asegúrate de que el servidor pueda acceder a la API de Google
- Revisa la configuración de firewall

### Rendimiento
- reCAPTCHA v3 es asíncrono y no afecta significativamente el rendimiento
- El tiempo de respuesta típico es de 100-300ms

## Seguridad

### Buenas Prácticas
1. **Nunca** compartas las claves privadas
2. Usa HTTPS en producción
3. Mantén las claves en variables de entorno
4. Monitorea los logs para intentos de bypass

### Variables de Entorno (Recomendado)
```python
import os
RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY')
``` 