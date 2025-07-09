# Sistema de Monedas - Megadominio.co

## Descripción

El sistema de monedas permite mostrar los precios en la moneda local del usuario:
- **Colombia**: Precios en Pesos Colombianos (COP)
- **Otros países**: Precios en Dólares Estadounidenses (USD)

## Funcionamiento

### 1. Detección de País
- **Perfil de usuario**: Si el usuario tiene configurado su país en el perfil
- **Geolocalización IP**: Detección automática basada en la dirección IP usando ip-api.com
- **Fallback**: Estados Unidos (USD) por defecto

### 2. Conversión de Precios
- Los precios base están almacenados en USD
- Para usuarios de Colombia, se convierten automáticamente a COP
- La conversión usa tasas de cambio actualizadas desde APIs externas

### 3. Tasas de Cambio
- **Fuente**: exchangerate-api.com (gratuito)
- **Actualización**: Automática cada hora
- **Almacenamiento**: Base de datos local para cache
- **Fallback**: Tasa fija de 4000 COP por USD

## Archivos Principales

### Modelos
- `accounts/models.py`: Modelo `ExchangeRate` para almacenar tasas
- `accounts/models.py`: Modelo `User` con campo `country`

### Utilidades
- `accounts/utils.py`: Funciones de detección de país y conversión
  - `get_user_country()`: Detecta el país del usuario
  - `get_currency_for_country()`: Obtiene la moneda según el país
  - `get_service_prices_for_user()`: Convierte precios para el usuario
  - `format_price()`: Formatea precios según la moneda

### Templates
- `accounts/templates/accounts/currency_indicator.html`: Indicador de moneda
- `accounts/templatetags/service_extras.py`: Template tags para monedas

### Comandos de Gestión
- `python manage.py update_exchange_rates`: Actualiza tasas de cambio
- `python manage.py update_exchange_rates --force`: Fuerza actualización

## Configuración de Administración

### Panel de Admin
- **ExchangeRate**: Gestionar tasas de cambio manualmente
- **User**: Ver/editar país de usuarios

### Automatización
Para actualizar tasas automáticamente, agregar a crontab:
```bash
# Actualizar tasas cada hora
0 * * * * cd /path/to/project && python manage.py update_exchange_rates
```

## API de Tasas de Cambio

### Fuente Principal: exchangerate-api.com
- **URL**: https://api.exchangerate-api.com/v4/latest/USD
- **Límites**: 1500 requests/mes (gratuito)
- **Respuesta**: JSON con tasas actuales

### Estructura de Respuesta
```json
{
  "base": "USD",
  "date": "2025-01-03",
  "rates": {
    "COP": 4007.74,
    "EUR": 0.85,
    ...
  }
}
```

## Personalización

### Agregar Nuevas Monedas
1. Actualizar `get_currency_for_country()` en `utils.py`
2. Agregar símbolos en `get_currency_symbol()` en template tags
3. Actualizar comando de actualización de tasas

### Cambiar Fuente de Tasas
1. Modificar `update_from_exchangerate_api()` en el comando
2. Agregar nueva función para la fuente deseada
3. Actualizar `get_exchange_rate()` en utils.py

## Formato de Precios

### USD (Dólares)
- Formato: `$1,234.56 USD`
- Decimales: 2 dígitos

### COP (Pesos Colombianos)
- Formato: `$1,234,567 COP`
- Decimales: Sin decimales (números enteros)

## Indicadores Visuales

### Indicador de Moneda
- Se muestra en el catálogo de servicios
- Informa al usuario sobre la moneda detectada
- Explica la conversión automática para usuarios de Colombia

### Estadísticas
- Contador de moneda local en la sección de estadísticas
- Muestra la moneda detectada (USD/COP)

## Troubleshooting

### Problemas Comunes

#### Tasas de cambio no actualizan
```bash
# Verificar conectividad
python manage.py update_exchange_rates --force

# Ver logs de errores
python manage.py shell -c "from accounts.models import ExchangeRate; print(ExchangeRate.objects.all())"
```

#### País mal detectado
- Verificar campo `country` en perfil de usuario
- Comprobar API de geolocalización IP
- Revisar logs de detección en `get_user_country()`

#### Precios no se convierten
- Verificar que existan tasas de cambio en BD
- Comprobar función `get_service_prices_for_user()`
- Revisar template tags en `service_extras.py`

## Extensiones Futuras

### Posibles Mejoras
1. **Más monedas**: EUR, MXN, ARS, etc.
2. **Cache avanzado**: Redis para tasas de cambio
3. **Múltiples fuentes**: Promedio de varias APIs
4. **Selección manual**: Permitir al usuario elegir moneda
5. **Histórico**: Guardar histórico de tasas para análisis

### APIs Alternativas
- **Fixer.io**: Más preciso, requiere API key
- **CurrencyAPI**: Alternativa confiable
- **Bank APIs**: APIs de bancos centrales 