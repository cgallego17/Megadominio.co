# 🎯 Panel de Administración de Servicios

## 📋 Descripción
Panel personalizado para gestionar servicios con iconos en megadominio.co. Interfaz moderna y fácil de usar para administrar tus servicios sin necesidad del admin de Django.

## 🚀 Acceso Rápido

### 🔑 Credenciales de Acceso
- **URL**: `http://localhost:8000/panel/login/`
- **Usuario**: `admin`
- **Contraseña**: `megadominio2024`

### 📱 URLs del Panel
- **Dashboard**: `/panel/dashboard/`
- **Gestionar Servicios**: `/panel/servicios/`
- **Crear Servicio**: `/panel/servicios/crear/`
- **Editar Servicio**: `/panel/servicios/{id}/editar/`
- **Eliminar Servicio**: `/panel/servicios/{id}/eliminar/`

## ✨ Características del Panel

### 🎨 Diseño Moderno
- ✅ Interfaz oscura con efectos glass
- ✅ Iconos FontAwesome integrados
- ✅ Diseño responsivo
- ✅ Animaciones suaves

### 🛠️ Funcionalidades Completas
- ✅ **CRUD Completo**: Crear, leer, actualizar y eliminar servicios
- ✅ **Selector Visual de Iconos**: 18 iconos predefinidos
- ✅ **Subida de Imágenes**: Soporte para iconos personalizados
- ✅ **Preview en Tiempo Real**: Vista previa del icono seleccionado
- ✅ **Validación de Formularios**: Campos requeridos y validación
- ✅ **Mensajes de Confirmación**: Feedback visual de acciones

## 🎯 Cómo Usar el Panel

### 1. 🔐 Iniciar Sesión
1. Ve a `http://localhost:8000/panel/login/`
2. Ingresa las credenciales:
   - Usuario: `admin`
   - Contraseña: `megadominio2024`
3. Serás redirigido al dashboard

### 2. 📊 Dashboard Principal
El dashboard muestra:
- **Estadísticas**: Número de servicios y proyectos
- **Acciones Rápidas**: Enlaces a gestión de servicios y proyectos
- **Navegación Intuitiva**: Breadcrumbs y menús claros

### 3. 📝 Gestionar Servicios

#### ➕ Crear Nuevo Servicio
1. Click en "Gestionar Servicios" → "Nuevo Servicio"
2. Completa el formulario:
   - **Nombre**: Título del servicio
   - **Descripción**: Descripción detallada
   - **Icono**: Selecciona de 18 opciones disponibles
   - **Imagen** (Opcional): Sube un archivo personalizado
3. Click "Crear Servicio"

#### ✏️ Editar Servicio Existente
1. En la lista de servicios, click "Editar"
2. Modifica los campos necesarios
3. El preview se actualiza en tiempo real
4. Click "Guardar Cambios"

#### 🗑️ Eliminar Servicio
1. Click "Eliminar" en el servicio deseado
2. Confirma la eliminación (⚠️ **irreversible**)
3. El servicio se elimina permanentemente

## 🎨 Iconos Disponibles

| Icono | Código FontAwesome | Uso Recomendado |
|-------|-------------------|-----------------|
| 🌐 | `fas fa-globe` | Páginas Web |
| 💻 | `fas fa-code` | Desarrollo |
| 🛒 | `fas fa-shopping-cart` | Ecommerce |
| 📧 | `fas fa-envelope` | Correos |
| 🖥️ | `fas fa-server` | Hosting |
| 🔗 | `fas fa-link` | Dominios |
| 🔒 | `fas fa-lock` | SSL |
| 🛡️ | `fas fa-shield-alt` | Seguridad |
| 🟦 | `fab fa-wordpress` | WordPress |
| 🟪 | `fab fa-woocommerce` | WooCommerce |
| ⚙️ | `fas fa-cogs` | Servicios Generales |
| 📱 | `fas fa-mobile-alt` | Apps Móviles |
| 🗄️ | `fas fa-database` | Base de Datos |
| ☁️ | `fas fa-cloud` | Cloud |
| 📊 | `fas fa-chart-line` | Analytics |
| 🎨 | `fas fa-paint-brush` | Diseño |
| 🚀 | `fas fa-rocket` | Optimización |
| 🎧 | `fas fa-headset` | Soporte |

## 🖼️ Imágenes Personalizadas

### 📋 Especificaciones Recomendadas
- **Formato**: SVG (recomendado) o PNG
- **Tamaño**: 64x64 píxeles
- **Fondo**: Transparente
- **Colores**: Monocromático (se aplicará filtro naranja)

### 🔄 Prioridad de Iconos
1. **Imagen personalizada** (si está subida)
2. **Icono FontAwesome** (si está seleccionado)
3. **Icono por defecto** (`fas fa-cogs`)

## 🎯 Frontend - Cómo se Muestran

Los iconos aparecen en el sitio web en:
- **Sección Servicios**: Página principal (`http://localhost:8000/`)
- **Diseño**: Contenedores glass con efecto hover
- **Color**: Naranja corporativo (#ff6600)
- **Tamaño**: 32px en contenedores de 80x80px

## 🔧 Configuración Técnica

### 📁 Archivos del Panel
```
adminpanel/
├── views.py           # Lógica del panel
├── urls.py            # URLs del panel
└── templates/adminpanel/
    ├── dashboard.html      # Dashboard principal
    ├── servicios_list.html # Lista de servicios
    ├── servicio_edit.html  # Editar servicio
    ├── servicio_create.html # Crear servicio
    └── servicio_delete.html # Eliminar servicio
```

### 🔗 Integración con Frontend
- **Modelo**: `servicios.models.Servicio`
- **Template**: `servicios/templates/servicios/home-clean.html`
- **Vista**: `servicios.views.home`

## 🛡️ Seguridad y Sesiones

### 🔐 Sistema de Autenticación
- **Sesión**: Sistema básico de sesiones de Django
- **Middleware**: Verificación en cada vista del panel
- **Logout**: Cierra sesión y limpia datos
- **Timeout**: La sesión permanece activa hasta logout manual

### 🚪 Cerrar Sesión
- Click en "Cerrar sesión" en cualquier página del panel
- O navega a `/panel/logout/`

## 🚀 Acceso Rápido

### 🖥️ URLs Principales
- **Sitio Web**: `http://localhost:8000/`
- **Panel Admin**: `http://localhost:8000/panel/login/`
- **Django Admin** (opcional): `http://localhost:8000/admin/`

### ⚡ Workflow Típico
1. **Acceder**: `/panel/login/` → Credenciales
2. **Gestionar**: Dashboard → "Gestionar Servicios"
3. **Editar**: Seleccionar servicio → "Editar" → Cambiar icono
4. **Verificar**: Abrir sitio web → Ver cambios en sección servicios

## 📞 Soporte y Troubleshooting

### ❓ Problemas Comunes

#### Los iconos no se muestran
- ✅ Verifica que FontAwesome esté cargado
- ✅ Revisa la consola del navegador
- ✅ Confirma que el servidor esté corriendo

#### No puedo acceder al panel
- ✅ Verifica las credenciales: `admin` / `megadominio2024`
- ✅ Asegúrate de estar en `/panel/login/`
- ✅ Limpia cookies del navegador

#### Los cambios no se reflejan
- ✅ Recarga la página del sitio web
- ✅ Verifica que guardaste los cambios
- ✅ Revisa que el servicio esté activo

### 🔄 Reiniciar Sistema
```bash
# Reiniciar servidor
python manage.py runserver

# Verificar migraciones
python manage.py migrate

# Crear superusuario (opcional)
python manage.py createsuperuser
```

## 🎉 ¡Panel Listo!

Tu panel personalizado está completamente funcional. Disfruta gestionando tus servicios con una interfaz moderna y fácil de usar.

**¡Los iconos se actualizan automáticamente en el frontend!** 🚀 