#!/bin/bash
set -e

# Configuración - Usando rutas ABSOLUTAS
BASE_DIR="$HOME/opt/odoo/odoo-from-13-to-18/arquitectura/odoo19"
BACKUP_BASE_DIR="$BASE_DIR/backup/out"
DB_CONTAINER="odoo-db19-test"

# Configuración del cliente
CLIENT_NAME="integraia_19"
CLIENT_DIR="$BASE_DIR/clientes/$CLIENT_NAME"
ODOO_CONF="$CLIENT_DIR/conf/odoo.cfg"

# Verificar que exista el directorio de backups
if [ ! -d "$BACKUP_BASE_DIR" ]; then
    echo "[ERROR] No existe el directorio: $BACKUP_BASE_DIR"
    exit 1
fi

# Buscar el backup más reciente automáticamente
LATEST_BACKUP=$(ls -td "$BACKUP_BASE_DIR"/backup_* 2>/dev/null | head -1)
if [ -n "$LATEST_BACKUP" ]; then
    BACKUP_DIR="$LATEST_BACKUP"
    echo "[INFO] Backup encontrado: $(basename $BACKUP_DIR)"
else
    echo "[ERROR] No hay backups disponibles en $BACKUP_BASE_DIR"
    echo "Backups existentes:"
    ls -la "$BACKUP_BASE_DIR"/ 2>/dev/null || echo "  (ninguno)"
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
    # Eliminar posibles comas y espacios (por si hay múltiples rutas)
    DATA_DIR=$(echo "$DATA_DIR" | cut -d',' -f1 | xargs)
fi

# Valores por defecto si no se encuentran en el cfg
DB_NAME=${DB_NAME:-dbintegraia_19}
DB_USER=${DB_USER:-integraia_19}
DATA_DIR=${DATA_DIR:-"$CLIENT_DIR/data"}

# Buscar los archivos del backup (usando la fecha del directorio)
BACKUP_DATE=$(basename "$BACKUP_DIR" | sed 's/backup_//')
DB_DUMP="$BACKUP_DIR/odoo_db_${BACKUP_DATE}.dump"
ADDONS_TAR="$BACKUP_DIR/odoo_addons_${BACKUP_DATE}.tar.gz"
FILESTORE_TAR="$BACKUP_DIR/odoo_filestore_${BACKUP_DATE}.tar.gz"

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[INFO]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
info() { echo -e "${BLUE}[DEBUG]${NC} $1"; }

# Verificar que exista el dump
if [ ! -f "$DB_DUMP" ]; then
    error "No se encuentra el dump: $DB_DUMP"
fi

log "=========================================="
log "Restaurando desde backup: $BACKUP_DATE"
log "Cliente: $CLIENT_NAME"
log "Base de datos destino: $DB_NAME"
log "Usuario DB: $DB_USER"
log "Data directory: $DATA_DIR"
log "=========================================="

# 1. Detener Odoo (si está corriendo)
log "Deteniendo Odoo para $CLIENT_NAME..."
pkill -f "odoo-bin.*--conf $ODOO_CONF" 2>/dev/null || warn "No se encontró proceso Odoo corriendo"
sleep 3

# 2. Crear directorios necesarios
log "Creando directorios necesarios..."
mkdir -p "$DATA_DIR"/{filestore,addons}
mkdir -p "$DATA_DIR/addons"/{oca,extra,enterprise}

# 3. Restaurar addons (desde archivo separado)
if [ -f "$ADDONS_TAR" ]; then
    log "Restaurando addons desde: $(basename "$ADDONS_TAR")"
    
    TEMP_ADDONS_DIR="/tmp/restore_addons_$$"
    mkdir -p "$TEMP_ADDONS_DIR"
    
    # Extraer addons
    tar --no-same-owner --no-same-permissions -xzf "$ADDONS_TAR" -C "$TEMP_ADDONS_DIR"
    
    # Buscar y clasificar módulos
    log "Buscando y clasificando addons..."
    
    # Buscar módulos por __manifest__.py
    while IFS= read -r manifest; do
        module_dir=$(dirname "$manifest")
        module_name=$(basename "$module_dir")
        
        # Determinar tipo por la ruta
        if [[ "$module_dir" =~ /oca/ ]]; then
            module_type="oca"
        elif [[ "$module_dir" =~ /enterprise/ ]]; then
            module_type="enterprise"
        else
            module_type="extra"
        fi
        
        dest_dir="$DATA_DIR/addons/$module_type/$module_name"
        [ -d "$dest_dir" ] && rm -rf "$dest_dir"
        cp -r "$module_dir" "$dest_dir"
        
        log "  ✅ Módulo: $module_name → $module_type"
    done < <(find "$TEMP_ADDONS_DIR" -name "__manifest__.py" 2>/dev/null || true)
    
    rm -rf "$TEMP_ADDONS_DIR"
    log "✅ Addons restaurados en $DATA_DIR/addons/"
else
    warn "No se encontró backup de addons: $ADDONS_TAR"
fi

# 4. Restaurar filestore
if [ -f "$FILESTORE_TAR" ]; then
    log "Restaurando filestore desde: $(basename "$FILESTORE_TAR")"
    
    TEMP_FILESTORE_DIR="/tmp/restore_filestore_$$"
    mkdir -p "$TEMP_FILESTORE_DIR"
    
    # Extraer filestore
    tar --no-same-owner --no-same-permissions -xzf "$FILESTORE_TAR" -C "$TEMP_FILESTORE_DIR"
    
    # Buscar el directorio filestore
    FILESTORE_BASE=$(find "$TEMP_FILESTORE_DIR" -type d -name "filestore" | head -1)
    
    if [ -n "$FILESTORE_BASE" ]; then
        ORIGINAL_DB_NAME=$(find "$FILESTORE_BASE" -maxdepth 1 -type d ! -path "$FILESTORE_BASE" | head -1 | xargs basename 2>/dev/null)
        
        if [ -n "$ORIGINAL_DB_NAME" ]; then
            log "Filestore original detectado: $ORIGINAL_DB_NAME"
            log "Renombrando a: $DB_NAME"
            
            rm -rf "$DATA_DIR/filestore/$DB_NAME"
            mkdir -p "$DATA_DIR/filestore"
            mv "$FILESTORE_BASE/$ORIGINAL_DB_NAME" "$DATA_DIR/filestore/$DB_NAME"
            
            log "✅ Filestore restaurado en $DATA_DIR/filestore/$DB_NAME"
        else
            warn "No se pudo determinar el nombre original del filestore"
        fi
    else
        warn "No se encontró el directorio filestore en el backup"
    fi
    
    rm -rf "$TEMP_FILESTORE_DIR"
else
    warn "No se encontró backup de filestore: $FILESTORE_TAR"
fi

# 5. Limpiar permisos
log "Ajustando permisos..."
chown -R $(whoami):$(whoami) "$DATA_DIR/addons/" 2>/dev/null || true
chmod -R 755 "$DATA_DIR/addons/" 2>/dev/null || true

# 6. Crear/verificar rol en PostgreSQL
log "Verificando rol '$DB_USER' en PostgreSQL..."

ROLE_EXISTS=$(docker exec $DB_CONTAINER psql -U odoo -d postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" 2>/dev/null || echo "0")

if [ "$ROLE_EXISTS" = "1" ]; then
    log "✅ El rol '$DB_USER' ya existe"
    # Actualizar contraseña
    docker exec $DB_CONTAINER psql -U odoo -d postgres -c "ALTER ROLE \"$DB_USER\" WITH LOGIN PASSWORD '$DB_PASSWORD';" 2>/dev/null || true
else
    log "Creando rol '$DB_USER'..."
    docker exec $DB_CONTAINER psql -U odoo -d postgres -c "CREATE ROLE \"$DB_USER\" WITH LOGIN PASSWORD '$DB_PASSWORD' CREATEDB;" 2>/dev/null || true
    log "✅ Rol '$DB_USER' creado"
fi

# 7. Restaurar base de datos
log "Restaurando base de datos $DB_NAME..."

# Eliminar base de datos existente
docker exec -e PGPASSWORD=$DB_PASSWORD $DB_CONTAINER psql -U $DB_USER -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='$DB_NAME';" 2>/dev/null || true
docker exec -e PGPASSWORD=$DB_PASSWORD $DB_CONTAINER dropdb -U $DB_USER --if-exists $DB_NAME 2>/dev/null || true
docker exec -e PGPASSWORD=$DB_PASSWORD $DB_CONTAINER createdb -U $DB_USER $DB_NAME

log "Restaurando dump de base de datos (puede tomar varios minutos)..."
set +e
docker exec -i -e PGPASSWORD=$DB_PASSWORD $DB_CONTAINER pg_restore \
    -U $DB_USER \
    -d $DB_NAME \
    --no-owner \
    --no-privileges \
    < "$DB_DUMP" 2>&1
PG_EXIT=$?
set -e

if [ $PG_EXIT -eq 0 ]; then
    log "✅ Base de datos restaurada correctamente"
else
    error "❌ Falló la restauración de la base de datos (código: $PG_EXIT)"
fi

# 8. Mostrar resumen
echo ""
log "=========================================="
log "✅ RESTAURACIÓN COMPLETADA"
log "=========================================="
log "Base de datos: $DB_NAME"
log "Usuario DB: $DB_USER"
log "Filestore: $DATA_DIR/filestore/$DB_NAME"
log "Addons OCA: $DATA_DIR/addons/oca"
log "Addons EXTRA: $DATA_DIR/addons/extra"
log "Puerto Odoo: $(grep '^http_port' $ODOO_CONF | awk -F '=' '{print $2}' | tr -d ' ')"
log ""
log "Para iniciar Odoo:"
echo "  cd $BASE_DIR/odoo/odoo"
echo "  python3 odoo-bin -c $ODOO_CONF"