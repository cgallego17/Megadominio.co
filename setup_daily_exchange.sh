#!/bin/bash

# 📅 CONFIGURACIÓN AUTOMÁTICA DE ACTUALIZACIÓN DIARIA DE TASAS DE CAMBIO
# Script para configurar cron job automáticamente

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar mensajes
show_message() {
    echo -e "${GREEN}✅ $1${NC}"
}

show_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

show_error() {
    echo -e "${RED}❌ $1${NC}"
}

show_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Función para verificar si un comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Función para detectar el intérprete de Python
detect_python() {
    if command_exists python; then
        echo "python"
    elif command_exists python3; then
        echo "python3"
    else
        show_error "Python no encontrado en el sistema"
        exit 1
    fi
}

# Función para detectar el directorio del proyecto
detect_project_dir() {
    if [ -f "manage.py" ]; then
        echo "$(pwd)"
    else
        show_error "No se encontró manage.py. Ejecute este script desde la raíz del proyecto Django."
        exit 1
    fi
}

# Función para verificar el entorno virtual
check_venv() {
    if [ ! -z "$VIRTUAL_ENV" ]; then
        echo "$VIRTUAL_ENV/bin/python"
    else
        echo "$(detect_python)"
    fi
}

# Función para probar el comando
test_command() {
    local python_cmd="$1"
    local project_dir="$2"
    
    show_info "Probando comando de actualización..."
    
    cd "$project_dir"
    if $python_cmd manage.py update_exchange_rates --help > /dev/null 2>&1; then
        show_message "Comando funciona correctamente"
        return 0
    else
        show_error "El comando no funciona. Verifique que el proyecto esté configurado correctamente."
        return 1
    fi
}

# Función para configurar cron job
setup_cron() {
    local python_cmd="$1"
    local project_dir="$2"
    local hour="$3"
    local log_file="$4"
    
    # Crear la entrada de cron
    local cron_entry="0 $hour * * * cd $project_dir && $python_cmd manage.py update_exchange_rates >> $log_file 2>&1"
    
    # Verificar si ya existe una entrada similar
    if crontab -l 2>/dev/null | grep -q "update_exchange_rates"; then
        show_warning "Ya existe una entrada de cron para update_exchange_rates"
        echo -e "${YELLOW}Entrada actual:${NC}"
        crontab -l 2>/dev/null | grep "update_exchange_rates"
        echo ""
        read -p "¿Desea reemplazarla? (s/n): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Ss]$ ]]; then
            # Remover entrada existente
            crontab -l 2>/dev/null | grep -v "update_exchange_rates" | crontab -
            show_message "Entrada anterior removida"
        else
            show_info "Configuración cancelada"
            exit 0
        fi
    fi
    
    # Agregar nueva entrada
    (crontab -l 2>/dev/null; echo "$cron_entry") | crontab -
    show_message "Cron job configurado exitosamente"
    
    # Mostrar la configuración
    echo -e "${BLUE}Configuración aplicada:${NC}"
    echo "  Hora: $hour:00 AM"
    echo "  Comando: $python_cmd manage.py update_exchange_rates"
    echo "  Directorio: $project_dir"
    echo "  Log: $log_file"
}

# Función principal
main() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}  CONFIGURACIÓN AUTOMÁTICA DE TASAS DE CAMBIO${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo ""
    
    # Verificar que estamos en el directorio correcto
    PROJECT_DIR=$(detect_project_dir)
    show_message "Directorio del proyecto: $PROJECT_DIR"
    
    # Detectar Python
    PYTHON_CMD=$(check_venv)
    show_message "Intérprete Python: $PYTHON_CMD"
    
    # Probar el comando
    if ! test_command "$PYTHON_CMD" "$PROJECT_DIR"; then
        exit 1
    fi
    
    # Configuración interactiva
    echo ""
    show_info "Configuración del cron job:"
    
    # Hora de ejecución
    read -p "Hora de ejecución diaria (0-23, default: 8): " HOUR
    HOUR=${HOUR:-8}
    
    # Validar hora
    if ! [[ "$HOUR" =~ ^[0-9]+$ ]] || [ "$HOUR" -lt 0 ] || [ "$HOUR" -gt 23 ]; then
        show_error "Hora inválida. Debe ser un número entre 0 y 23."
        exit 1
    fi
    
    # Archivo de log
    read -p "Archivo de log (default: /var/log/exchange_rates.log): " LOG_FILE
    LOG_FILE=${LOG_FILE:-/var/log/exchange_rates.log}
    
    # Verificar permisos de escritura para el log
    LOG_DIR=$(dirname "$LOG_FILE")
    if [ ! -w "$LOG_DIR" ]; then
        show_warning "No tiene permisos de escritura en $LOG_DIR"
        read -p "¿Usar archivo de log en el directorio del proyecto? (s/n): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Ss]$ ]]; then
            LOG_FILE="$PROJECT_DIR/exchange_rates.log"
            show_message "Usando archivo de log: $LOG_FILE"
        else
            show_error "Configuración cancelada"
            exit 1
        fi
    fi
    
    # Confirmación
    echo ""
    echo -e "${YELLOW}Configuración a aplicar:${NC}"
    echo "  Hora: $HOUR:00 AM"
    echo "  Directorio: $PROJECT_DIR"
    echo "  Python: $PYTHON_CMD"
    echo "  Log: $LOG_FILE"
    echo ""
    
    read -p "¿Confirma la configuración? (s/n): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        setup_cron "$PYTHON_CMD" "$PROJECT_DIR" "$HOUR" "$LOG_FILE"
        
        # Mostrar cron jobs actuales
        echo ""
        show_info "Cron jobs configurados:"
        crontab -l | grep -E "(update_exchange_rates|#)"
        
        # Instrucciones finales
        echo ""
        show_message "¡Configuración completada!"
        echo ""
        echo -e "${BLUE}Próximos pasos:${NC}"
        echo "1. Verificar que el sistema funciona:"
        echo "   python manage.py check_exchange_system --verbose"
        echo ""
        echo "2. Monitorear el log de ejecuciones:"
        echo "   tail -f $LOG_FILE"
        echo ""
        echo "3. Probar manualmente:"
        echo "   python manage.py update_exchange_rates"
        echo ""
        echo -e "${GREEN}El sistema ejecutará automáticamente todos los días a las $HOUR:00 AM${NC}"
        
    else
        show_info "Configuración cancelada"
        exit 0
    fi
}

# Verificar que el script se ejecute con bash
if [ -z "$BASH_VERSION" ]; then
    echo "Este script requiere bash. Ejecute con: bash setup_daily_exchange.sh"
    exit 1
fi

# Ejecutar función principal
main "$@" 