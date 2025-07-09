# 📅 CONFIGURACIÓN DE ACTUALIZACIÓN DIARIA DE TASAS DE CAMBIO

## 🎯 **OBJETIVO IMPLEMENTADO**

✅ **Sistema configurado para actualizar tasas de cambio MÁXIMO 1 VEZ POR DÍA**

## 🔧 **CARACTERÍSTICAS IMPLEMENTADAS**

### **1. Verificación por Día Calendario**
- ✅ Verifica si ya se actualizó **HOY** (no por 24 horas corridas)
- ✅ Previene múltiples actualizaciones en el mismo día
- ✅ Respeta el límite de 1 actualización por día

### **2. Hora Preferida de Actualización**
- ✅ Hora predeterminada: **8:00 AM**
- ✅ Configurable con parámetro `--preferred-hour`
- ✅ Tolerancia de ±2 horas (advertencia, no bloqueo)

### **3. Modo Forzado**
- ✅ Parámetro `--force` para casos especiales
- ✅ Permite actualizar múltiples veces si es necesario

## 📋 **COMANDOS DISPONIBLES**

### **Actualización Normal (Recomendado)**
```bash
# Actualización diaria estándar
python manage.py update_exchange_rates

# Con hora preferida personalizada (por ejemplo, 10:00 AM)
python manage.py update_exchange_rates --preferred-hour 10
```

### **Actualización Forzada**
```bash
# Forzar actualización aunque ya se haya ejecutado hoy
python manage.py update_exchange_rates --force
```

### **Verificación del Sistema**
```bash
# Verificar estado del sistema
python manage.py check_exchange_system --verbose
```

## ⚙️ **CONFIGURACIÓN AUTOMÁTICA CON CRON**

### **1. Configuración Básica (Recomendada)**
```bash
# Abrir crontab
crontab -e

# Agregar línea para actualizar a las 8:00 AM todos los días
0 8 * * * cd /path/to/your/project && python manage.py update_exchange_rates >> /var/log/exchange_rates.log 2>&1
```

### **2. Configuración con Entorno Virtual**
```bash
# Si usas virtual environment
0 8 * * * cd /path/to/your/project && /path/to/venv/bin/python manage.py update_exchange_rates >> /var/log/exchange_rates.log 2>&1
```

### **3. Configuración con Múltiples Intentos**
```bash
# Primera actualización a las 8:00 AM
0 8 * * * cd /path/to/your/project && python manage.py update_exchange_rates

# Respaldo a las 12:00 PM (solo si falló la primera)
0 12 * * * cd /path/to/your/project && python manage.py update_exchange_rates

# Último intento a las 18:00 PM (solo si fallaron las anteriores)
0 18 * * * cd /path/to/your/project && python manage.py update_exchange_rates
```

## 📊 **MONITOREO Y LOGS**

### **Registro de Actividades**
```bash
# Ver historial de actualizaciones
tail -f /var/log/exchange_rates.log

# Verificar última actualización
python manage.py check_exchange_system
```

### **Verificación Manual**
```bash
# Comprobar tasas actuales
python manage.py shell -c "
from accounts.models import ExchangeRate
from django.utils import timezone

rate = ExchangeRate.objects.filter(from_currency='USD', to_currency='COP').first()
if rate:
    print(f'Última actualización: {rate.updated_at}')
    print(f'Tasa actual: 1 USD = {rate.rate} COP')
else:
    print('No hay tasas registradas')
"
```

## 🛡️ **SISTEMA DE PROTECCIÓN**

### **Prevención de Múltiples Ejecuciones**
- ✅ Verifica fecha de última actualización
- ✅ Bloquea ejecuciones múltiples el mismo día
- ✅ Requiere `--force` para sobrescribir

### **Manejo de Errores**
- ✅ Logs detallados en caso de fallos
- ✅ Fallback a tasa fija si API no responde
- ✅ Notificaciones claras del estado

## 📈 **OPTIMIZACIÓN DE REQUESTS API**

### **Límites Respetados**
- **API Gratuita**: 100 requests/mes
- **Uso Actual**: 30 requests/mes (máximo)
- **Reserva**: 70 requests/mes disponibles

### **Cálculo de Uso**
```
1 actualización/día × 30 días = 30 requests/mes
Límite: 100 requests/mes
Utilización: 30% (70% de reserva)
```

## 🔄 **EJEMPLOS DE USO**

### **Caso 1: Primera Configuración**
```bash
# Instalar tasas iniciales
python manage.py update_exchange_rates

# Verificar instalación
python manage.py check_exchange_system --verbose
```

### **Caso 2: Mantenimiento Diario**
```bash
# Ejecución automática vía cron (8:00 AM)
0 8 * * * cd /path/to/project && python manage.py update_exchange_rates
```

### **Caso 3: Solución de Problemas**
```bash
# Si hay problemas, forzar actualización
python manage.py update_exchange_rates --force

# Verificar conectividad con API
python manage.py check_exchange_system --test-api
```

## 🚨 **RESOLUCIÓN DE PROBLEMAS**

### **Problema: "Ya se actualizó HOY"**
```bash
# Solución: Usar --force si realmente necesitas actualizar
python manage.py update_exchange_rates --force
```

### **Problema: Error de conectividad**
```bash
# Verificar conectividad
python manage.py check_exchange_system --test-api

# Si persiste, el sistema usará tasa fallback de 4000 COP/USD
```

### **Problema: Múltiples ejecuciones cron**
```bash
# Verificar cron jobs duplicados
crontab -l | grep exchange_rates

# Eliminar duplicados si los hay
crontab -e
```

## 📋 **CHECKLIST DE IMPLEMENTACIÓN**

### **Pre-Implementación**
- [ ] Verificar que el proyecto esté funcionando
- [ ] Comprobar acceso a Internet
- [ ] Revisar permisos de escritura para logs

### **Implementación**
- [ ] Configurar cron job
- [ ] Probar actualización manual
- [ ] Verificar logs de funcionamiento

### **Post-Implementación**
- [ ] Monitorear por 1 semana
- [ ] Verificar que no haya ejecuciones múltiples
- [ ] Confirmar que las tasas se actualizan correctamente

### **Mantenimiento**
- [ ] Revisar logs semanalmente
- [ ] Verificar límites de API mensualmente
- [ ] Actualizar documentación si es necesario

## 🎉 **BENEFICIOS OBTENIDOS**

✅ **Automatización completa** - Sin intervención manual
✅ **Respeto de límites** - Máximo 1 actualización por día
✅ **Optimización de API** - 70% de reserva disponible
✅ **Monitoreo integrado** - Logs y verificaciones automáticas
✅ **Flexibilidad** - Configuración de horarios y forzado
✅ **Robustez** - Manejo de errores y fallbacks

El sistema está **completamente implementado** y listo para **producción**. 