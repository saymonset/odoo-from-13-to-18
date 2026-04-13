#!/bin/bash
set -e

# Configuración - Usando Docker para PostgreSQL
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_BASE_DIR="$SCRIPT_DIR/out"
DB_CONTAINER="odoo-db19-test"  # Tu contenedor de PostgreSQL
SUPERUSER="odoo"  # El superuser en tu contenedor es 'odoo'

# El script recibe el cliente como parámetro
CLIENT_NAME="${1:-integraia_19}"  # Por defecto integraia_19
CLIENT_DIR="$HOME/opt/odoo/odoo-from-13-to-18/arquitectura/odoo19/clientes/$CLIENT_NAME"
ODOO_CONF="$CLIENT_DIR/conf/odoo.cfg"

# Verificar que exista el cliente
if [ ! -f "$ODOO_CONF" ]; then
    echo "❌ Cliente no encontrado: $CLIENT_NAME"
    echo "Clientes disponibles:"
    ls -1 "$HOME/opt/odoo/odoo-from-13-to-18/arquitectura/odoo19/clientes/"
    exit 1
fi

# Verificar que el contenedor de PostgreSQL esté corriendo
if ! docker ps | grep -q "$DB_CONTAINER"; then
    echo "❌ El contenedor $DB_CONTAINER no está corriendo"
    echo "Inícialo con: docker start $DB_CONTAINER"
    exit 1
fi

# Extraer variables del archivo de configuración del cliente
if [ -f "$ODOO_CONF" ]; then
    DB_NAME=$(grep -E '^db_name\s*=' "$ODOO_CONF" | awk -F '=' '{print $2}' | tr -d ' ' | tr -d '\r')
    DB_USER=$(grep -E '^db_user\s*=' "$ODOO_CONF" | awk -F '=' '{print $2}' | tr -d ' ' | tr -d '\r')
    DB_PASSWORD=$(grep -E '^db_password\s*=' "$ODOO_CONF" | awk -F '=' '{print $2}' | tr -d ' ' | tr -d '\r')
    DATA_DIR=$(grep -E '^data_dir\s*=' "$ODOO_CONF" | awk -F '=' '{print $2}' | tr -d ' ' | tr -d '\r')
    # Expandir ~ a home
    DATA_DIR="${DATA_DIR/#\~/$HOME}"
fi

DB_NAME=${DB_NAME:-dbodoo19}
DB_USER=${DB_USER:-odoo}
DATA_DIR=${DATA_DIR:-"$CLIENT_DIR/data"}

# Crear directorio de backup con timestamp
TIMESTAMP=$(date '+%Y-%m-%d_%H-%M-%S')
BACKUP_DIR="$BACKUP_BASE_DIR/backup_$TIMESTAMP"
mkdir -p "$BACKUP_DIR"

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
info() { echo -e "${BLUE}[INFO]${NC} $1"; }

usage() {
    echo "Uso: $0 [cliente] [opciones]"
    echo ""
    echo "Clientes disponibles:"
    ls -1 "$HOME/opt/odoo/odoo-from-13-to-18/arquitectura/odoo19/clientes/" | sed 's/^/  - /'
    echo ""
    echo "Opciones:"
    echo "  --no-filestore      No incluir filestore en el backup"
    echo "  --no-addons         No incluir addons en el backup"
    echo "  -h, --help          Mostrar ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0 integraia_19                     # Backup completo"
    echo "  $0 integraia_19 --no-filestore      # Backup sin filestore"
    echo "  $0 hoteljumpjibe_19                 # Backup para otro cliente"
    exit 0
}

backup_database() {
    info "Respaldando base de datos $DB_NAME..."
    
    local dump_file="$BACKUP_DIR/odoo_db_${TIMESTAMP}.dump"
    
    docker exec -e PGPASSWORD=$DB_PASSWORD $DB_CONTAINER pg_dump \
        -U $DB_USER \
        -F c \
        -f "/tmp/odoo_db_${TIMESTAMP}.dump" \
        "$DB_NAME"
    
    docker cp "$DB_CONTAINER:/tmp/odoo_db_${TIMESTAMP}.dump" "$dump_file"
    docker exec $DB_CONTAINER rm -f "/tmp/odoo_db_${TIMESTAMP}.dump"
    
    local dump_size=$(du -h "$dump_file" | cut -f1)
    log "✅ Base de datos respaldada: $(basename "$dump_file") ($dump_size)"
}

backup_addons_separate() {
    info "Respaldando addons por separado..."
    
    local addons_file="$BACKUP_DIR/odoo_addons_${TIMESTAMP}.tar.gz"
    local temp_dir="/tmp/backup_addons_$$"
    
    mkdir -p "$temp_dir"
    
    local has_content=false
    
    # 1. Copiar addons OCA (si existen)
    if [ -d "$DATA_DIR/addons/oca" ] && [ "$(ls -A "$DATA_DIR/addons/oca" 2>/dev/null)" ]; then
        info "  Copiando addons OCA..."
        mkdir -p "$temp_dir/oca"
        cp -r "$DATA_DIR/addons/oca"/* "$temp_dir/oca/"
        log "    ✅ Addons OCA copiados"
        has_content=true
    else
        warn "  No se encontraron addons OCA"
    fi
    
    # 2. Copiar addons EXTRA (si existen)
    if [ -d "$DATA_DIR/addons/extra" ] && [ "$(ls -A "$DATA_DIR/addons/extra" 2>/dev/null)" ]; then
        info "  Copiando addons EXTRA..."
        mkdir -p "$temp_dir/extra"
        cp -r "$DATA_DIR/addons/extra"/* "$temp_dir/extra/"
        log "    ✅ Addons EXTRA copiados"
        has_content=true
    else
        warn "  No se encontraron addons EXTRA"
    fi
    
    # 3. Copiar addons ENTERPRISE (si existen)
    if [ -d "$DATA_DIR/addons/enterprise" ] && [ "$(ls -A "$DATA_DIR/addons/enterprise" 2>/dev/null)" ]; then
        info "  Copiando addons ENTERPRISE..."
        mkdir -p "$temp_dir/enterprise"
        cp -r "$DATA_DIR/addons/enterprise"/* "$temp_dir/enterprise/"
        log "    ✅ Addons ENTERPRISE copiados"
        has_content=true
    else
        warn "  No se encontraron addons ENTERPRISE"
    fi
    
    # 4. Crear el tar.gz de addons
    if [ "$has_content" = true ]; then
        tar -czf "$addons_file" -C "$temp_dir" .
        local addons_size=$(du -h "$addons_file" | cut -f1)
        log "✅ Addons empaquetados: $(basename "$addons_file") ($addons_size)"
        
        # Mostrar estructura
        info "  Estructura del backup de addons:"
        tar -tzf "$addons_file" | head -10 | sed 's/^/    /'
        if [ $(tar -tzf "$addons_file" | wc -l) -gt 10 ]; then
            echo "    ... y más"
        fi
    else
        warn "No hay addons para respaldar"
        rm -f "$addons_file"
    fi
    
    rm -rf "$temp_dir"
}

backup_filestore_separate() {
    info "Respaldando filestore por separado..."
    
    local filestore_file="$BACKUP_DIR/odoo_filestore_${TIMESTAMP}.tar.gz"
    local temp_dir="/tmp/backup_filestore_$$"
    
    mkdir -p "$temp_dir"
    
    # Copiar filestore
    if [ -d "$DATA_DIR/filestore/$DB_NAME" ]; then
        info "  Copiando filestore de $DB_NAME..."
        mkdir -p "$temp_dir/filestore"
        cp -r "$DATA_DIR/filestore/$DB_NAME" "$temp_dir/filestore/"
        
        # Crear el tar.gz de filestore
        tar -czf "$filestore_file" -C "$temp_dir" .
        local filestore_size=$(du -h "$filestore_file" | cut -f1)
        log "✅ Filestore empaquetado: $(basename "$filestore_file") ($filestore_size)"
    else
        warn "No se encontró filestore para $DB_NAME en $DATA_DIR/filestore/$DB_NAME"
        rm -f "$filestore_file"
    fi
    
    rm -rf "$temp_dir"
}

backup_config() {
    info "Respaldando configuración..."
    
    local config_file="$BACKUP_DIR/odoo_config_${TIMESTAMP}.conf"
    cp "$ODOO_CONF" "$config_file"
    log "✅ Configuración respaldada: $(basename "$config_file")"
}

cleanup_old_backups() {
    local keep_days=${1:-30}
    info "Limpiando backups antiguos (más de $keep_days días)..."
    
    local deleted=0
    for backup in $(find "$BACKUP_BASE_DIR" -maxdepth 1 -type d -name "backup_*" -mtime +$keep_days 2>/dev/null); do
        rm -rf "$backup"
        log "  Eliminado: $(basename "$backup")"
        ((deleted++))
    done
    
    if [ $deleted -gt 0 ]; then
        log "✅ $deleted backups antiguos eliminados"
    else
        info "No hay backups antiguos para eliminar"
    fi
}

# Procesar argumentos
INCLUDE_FILESTORE=true
INCLUDE_ADDONS=true

# Si el primer argumento no empieza con -, es el nombre del cliente
if [[ $1 && $1 != -* ]]; then
    CLIENT_NAME="$1"
    CLIENT_DIR="$HOME/opt/odoo/odoo-from-13-to-18/arquitectura/odoo19/clientes/$CLIENT_NAME"
    ODOO_CONF="$CLIENT_DIR/conf/odoo.cfg"
    shift
fi

# Procesar opciones
while [ $# -gt 0 ]; do
    case $1 in
        --no-filestore)
            INCLUDE_FILESTORE=false
            shift
            ;;
        --no-addons)
            INCLUDE_ADDONS=false
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            error "Opción desconocida: $1"
            ;;
    esac
done

# Re-leer configuración después de posible cambio de cliente
if [ -f "$ODOO_CONF" ]; then
    DB_NAME=$(grep -E '^db_name\s*=' "$ODOO_CONF" | awk -F '=' '{print $2}' | tr -d ' ' | tr -d '\r')
    DB_USER=$(grep -E '^db_user\s*=' "$ODOO_CONF" | awk -F '=' '{print $2}' | tr -d ' ' | tr -d '\r')
    DB_PASSWORD=$(grep -E '^db_password\s*=' "$ODOO_CONF" | awk -F '=' '{print $2}' | tr -d ' ' | tr -d '\r')
    DATA_DIR=$(grep -E '^data_dir\s*=' "$ODOO_CONF" | awk -F '=' '{print $2}' | tr -d ' ' | tr -d '\r')
    DATA_DIR="${DATA_DIR/#\~/$HOME}"
fi

# Verificar que la base de datos existe
info "Verificando conexión a la base de datos $DB_NAME..."
if ! docker exec -e PGPASSWORD=$DB_PASSWORD $DB_CONTAINER psql -U $DB_USER -d postgres -c "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1; then
    error "La base de datos $DB_NAME no existe en el contenedor"
fi

echo ""
info "=========================================="
info "Iniciando backup para cliente: $CLIENT_NAME"
info "Base de datos: $DB_NAME"
info "Data directory: $DATA_DIR"
info "Backup directory: $BACKUP_DIR"
info "Timestamp: $TIMESTAMP"
info "=========================================="
echo ""

# Realizar backup
backup_database

if [ "$INCLUDE_ADDONS" = true ]; then
    backup_addons_separate
fi

if [ "$INCLUDE_FILESTORE" = true ]; then
    backup_filestore_separate
fi

backup_config

# Crear archivo de información del backup
cat > "$BACKUP_DIR/backup_info.txt" << EOF
Backup Information
==================
Cliente: $CLIENT_NAME
Fecha: $TIMESTAMP
Base de datos: $DB_NAME
Usuario DB: $DB_USER
Data directory: $DATA_DIR
Incluye filestore: $INCLUDE_FILESTORE
Incluye addons: $INCLUDE_ADDONS

Archivos generados:
- odoo_db_${TIMESTAMP}.dump
- odoo_addons_${TIMESTAMP}.tar.gz
- odoo_filestore_${TIMESTAMP}.tar.gz
- odoo_config_${TIMESTAMP}.conf
EOF

echo ""
log "=========================================="
log "✅ BACKUP COMPLETADO EXITOSAMENTE"
log "=========================================="
info "Cliente: $CLIENT_NAME"
info "Base de datos: $DB_NAME"
info "Directorio de backup: $BACKUP_DIR"
info "Archivos generados:"
ls -lh "$BACKUP_DIR" | tail -n +2 | awk '{print "  - " $9 " (" $5 ")"}'
echo ""

# Mostrar resumen de addons si existen
if [ -f "$BACKUP_DIR/odoo_addons_${TIMESTAMP}.tar.gz" ]; then
    info "Contenido del backup de addons:"
    tar -tzf "$BACKUP_DIR/odoo_addons_${TIMESTAMP}.tar.gz" | head -20 | sed 's/^/  /'
    local total_modules=$(tar -tzf "$BACKUP_DIR/odoo_addons_${TIMESTAMP}.tar.gz" | grep -c "__manifest__.py" || echo "0")
    if [ "$total_modules" -gt 0 ]; then
        log "  Total de módulos encontrados: $total_modules"
    fi
fi

# Limpiar backups antiguos (opcional, mantener últimos 30 días)
cleanup_old_backups 30