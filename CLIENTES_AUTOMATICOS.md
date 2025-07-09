# Creación Automática de Clientes

## Descripción

Esta funcionalidad permite que cuando un usuario complete una compra y quede registrado en el sistema, automáticamente se cree como cliente en la nueva sección de "Clientes y Ventas" del panel de administración.

## Funcionalidades Implementadas

### 1. Creación Automática en Checkout

Cuando un usuario completa una orden en el checkout (ya sea con pago manual o con Wompi), automáticamente se crea:

- **Cliente**: Con la información del usuario o datos de facturación
- **Venta**: Registro de la transacción comercial
- **Detalles de Venta**: Items específicos de la orden

### 2. Creación Automática en Webhooks de Wompi

Cuando se recibe una notificación de pago exitoso desde Wompi, se crea automáticamente:

- **Cliente**: Si no existe previamente
- **Venta**: Con el estado "completada"
- **Detalles de Venta**: Todos los items de la orden

### 3. Procesamiento de Órdenes Existentes

Para migrar datos existentes, se incluye:

- **Función de procesamiento masivo**: `process_existing_orders_to_clients()`
- **Comando de gestión**: `python manage.py process_orders_to_clients`
- **Script de prueba**: `test_client_creation.py`

## Flujo de Funcionamiento

### Para Usuarios Registrados

1. Usuario completa checkout
2. Se crea la orden en el sistema
3. **Automáticamente se crea/actualiza el cliente** con:
   - Nombre completo del usuario
   - Email del usuario
   - Teléfono (si está disponible)
   - Empresa (si está disponible)
   - Dirección (si está disponible)
   - Estado: "activo"
   - Notas: "Cliente creado automáticamente desde orden #[número]"

### Para Usuarios Anónimos

1. Usuario anónimo completa checkout con datos de facturación
2. Se crea la orden en el sistema
3. **Automáticamente se crea el cliente** con:
   - Nombre de facturación
   - Email de facturación
   - Dirección de facturación
   - Estado: "activo"
   - Notas: "Cliente creado automáticamente desde orden #[número] (compra anónima)"

### Creación de Ventas

Para cada orden completada, se crea automáticamente:

- **Venta** con:
  - Número de factura = Número de orden
  - Cliente asociado
  - Estado: "completada" (si la orden está completada) o "pendiente"
  - Método de pago: "tarjeta" (por defecto)
  - Subtotal, impuestos, descuento, valor total
  - Descripción: "Orden #[número]"
  - Notas de la orden

### Creación de Detalles de Venta

Para cada item de la orden, se crea automáticamente:

- **Detalle de Venta** con:
  - Venta asociada
  - Nombre del servicio
  - Descripción: "[Servicio] - [Ciclo de facturación]"
  - Cantidad
  - Precio unitario
  - Subtotal

## Archivos Modificados

### 1. `accounts/views.py`
- **Importaciones agregadas**: `Cliente`, `Venta`, `DetalleVenta`
- **Función `create_or_update_client_from_order()`**: Crea/actualiza clientes desde órdenes
- **Función `process_existing_orders_to_clients()`**: Procesamiento masivo
- **Función `checkout()` modificada**: Llama a la creación automática
- **Función `wompi_webhook()`**: Procesa webhooks de Wompi

### 2. `accounts/services.py`
- **Función `update_transaction_status()` modificada**: Crea clientes cuando se aprueba transacción

### 3. `accounts/management/commands/process_orders_to_clients.py`
- **Comando de gestión**: Para procesar órdenes existentes

### 4. `test_client_creation.py`
- **Script de prueba**: Para verificar la funcionalidad

## Uso

### Procesamiento Automático

La funcionalidad es completamente automática. Cuando un usuario complete una compra:

1. Se crea la orden normalmente
2. **Automáticamente** se crea el cliente en el sistema de clientes
3. Se crea la venta correspondiente
4. Se crean los detalles de venta

### Procesamiento de Órdenes Existentes

Para procesar órdenes que ya existen en el sistema:

```bash
# Procesar todas las órdenes completadas
python manage.py process_orders_to_clients

# Modo dry-run (solo mostrar qué se haría)
python manage.py process_orders_to_clients --dry-run
```

### Pruebas

Para probar la funcionalidad:

```bash
# Ejecutar script de prueba
python test_client_creation.py
```

## Beneficios

1. **Automatización completa**: No requiere intervención manual
2. **Consistencia de datos**: Todos los clientes quedan registrados uniformemente
3. **Trazabilidad**: Cada venta está vinculada a una orden específica
4. **Flexibilidad**: Funciona tanto para usuarios registrados como anónimos
5. **Migración de datos**: Permite procesar órdenes existentes

## Notas Importantes

- Los clientes se crean con estado "activo" por defecto
- Si ya existe un cliente con el mismo email, se actualiza la información
- Las ventas se crean con el número de orden como número de factura
- Los detalles de venta incluyen información del ciclo de facturación
- Se manejan errores graciosamente sin interrumpir el proceso de checkout

## Logs

La funcionalidad incluye logging detallado:

- Creación exitosa de clientes
- Errores en la creación de clientes
- Procesamiento de webhooks
- Procesamiento masivo de órdenes

Los logs se pueden encontrar en los archivos de log de Django con el logger `accounts.views`. 