# 🛒 Funcionalidad del Carrito - Guía de Uso

## ✅ Funcionalidades Implementadas

### 1. Agregar al Carrito
- **Ubicación**: Página de detalles del servicio (`/accounts/services/<slug>/`)
- **Funcionalidad**: 
  - Selección de ciclo de facturación (mensual, anual, etc.)
  - Cantidad de servicios
  - Dominio (si es requerido)
  - Notas adicionales
  - Cálculo automático del total

### 2. Contador del Carrito
- **Ubicación**: Sidebar del panel cliente
- **Funcionalidad**:
  - Muestra el número de items en el carrito
  - Se actualiza automáticamente al agregar/quitar items
  - Disponible en todas las páginas del panel cliente

### 3. Vista del Carrito
- **Ubicación**: `/accounts/cart/`
- **Funcionalidad**:
  - Lista de todos los items en el carrito
  - Actualización de cantidades
  - Eliminación de items
  - Cálculo del total

### 4. Proceso de Checkout
- **Ubicación**: `/accounts/checkout/`
- **Funcionalidad**:
  - Formulario de información de facturación
  - Resumen de la orden
  - Creación de la orden

## 🔧 Componentes Técnicos

### Modelos
- `Cart`: Carrito de compras por usuario
- `CartItem`: Items individuales del carrito
- `Order`: Órdenes de compra
- `OrderItem`: Items de una orden

### Vistas
- `add_to_cart`: Agregar servicio al carrito (AJAX)
- `cart_view`: Vista del carrito
- `update_cart_item`: Actualizar cantidad (AJAX)
- `remove_from_cart`: Eliminar item (AJAX)
- `checkout`: Proceso de checkout

### Context Processor
- `cart_context`: Proporciona `cart_items_count` a todos los templates

## 🧪 Cómo Probar

### 1. Iniciar Sesión
```bash
# Ejecutar servidor
python manage.py runserver

# Ir a http://localhost:8000/accounts/login/
# Usuario: cliente_demo
# Contraseña: (la que hayas configurado)
```

### 2. Navegar al Catálogo
- Ir a "Catálogo de Servicios" en el sidebar
- Seleccionar un servicio
- Hacer clic en "Ver Detalles"

### 3. Agregar al Carrito
- Seleccionar ciclo de facturación
- Ajustar cantidad
- Agregar dominio si es requerido
- Hacer clic en "Agregar al Carrito"
- Verificar que aparece el toast de éxito
- Verificar que el contador del carrito se actualiza

### 4. Ver Carrito
- Hacer clic en "Carrito" en el sidebar
- Verificar que los items aparecen correctamente
- Probar actualizar cantidades
- Probar eliminar items

### 5. Checkout
- Hacer clic en "Proceder al Checkout"
- Completar información de facturación
- Crear orden

## 🎨 Características de UI/UX

### Mensajes Toast
- Notificaciones elegantes en la esquina superior derecha
- Colores apropiados (verde para éxito, rojo para error)
- Auto-desaparición después de 4 segundos

### Contador del Carrito
- Badge naranja en el sidebar
- Actualización en tiempo real
- Visible en todas las páginas

### Formulario de Agregar al Carrito
- Cálculo automático del total
- Validación de campos requeridos
- Botón con loading state
- Diseño responsive

## 🔍 Verificación de Funcionalidad

### Checklist de Pruebas
- [ ] El contador del carrito se muestra correctamente
- [ ] Se pueden agregar servicios al carrito
- [ ] El toast de éxito aparece al agregar
- [ ] El contador se actualiza automáticamente
- [ ] La vista del carrito muestra los items
- [ ] Se pueden actualizar cantidades
- [ ] Se pueden eliminar items
- [ ] El checkout funciona correctamente
- [ ] Se crean las órdenes correctamente

## 🐛 Posibles Problemas

### Si el contador no se actualiza:
1. Verificar que el context processor está configurado
2. Verificar que el servidor se reinició después de agregar el context processor
3. Verificar que el usuario tiene permisos de cliente

### Si AJAX no funciona:
1. Verificar que el CSRF token está presente
2. Verificar que las URLs están correctas
3. Verificar la consola del navegador para errores

### Si no aparecen servicios:
1. Ejecutar `python manage.py shell` y verificar que hay servicios:
   ```python
   from accounts.models import PurchasableService
   print(PurchasableService.objects.filter(is_active=True).count())
   ```

## 📝 Próximas Mejoras

- [ ] Integración con sistema de pagos
- [ ] Notificaciones por email
- [ ] Historial de órdenes más detallado
- [ ] Facturación automática
- [ ] Descuentos y cupones 