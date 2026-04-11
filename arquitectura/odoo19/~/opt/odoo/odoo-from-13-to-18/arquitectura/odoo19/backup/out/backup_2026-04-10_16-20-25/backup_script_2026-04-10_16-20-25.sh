#!/bin/bash
set -e

# ============================================
# CONFIGURACIÓN FÁCIL DE MODIFICAR
# Solo cambia los valores de esta sección
# ============================================

# Rutas principales
BASE_DIR="~/opt/odoo/odoo-from-13-to-18/arquitectura/odoo19/clientes/integraia_19_delete"
BACKUP_BASE_DIR="~/opt/odoo/odoo-from-13-to-18/arquitectura/odoo19/backup/out"

# Datos de la base de datos
DB_CONTAINER="odoo-db19-n8n"  # Verifica si este es el contenedor correcto
DB_NAME="dbintegraia_19_delete"
DB_USER="integraia_19_delete"

# Configuración de backup
RETENTION_DAYS=7

# ============================================
# NO CAMBIES NADA DE AQUÍ EN ADELANTE
# ============================================

DATE=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_DIR="$BACKUP_BASE_DIR/backup_$DATE"

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

# Crear directorio de backup
mkdir -p $BACKUP_DIR

log "=========================================="
log "Iniciando Backup - $DATE"
log "=========================================="

# 1. Backup de base de datos
log "📦 Backup de base de datos Odoo..."
docker exec $DB_CONTAINER pg_dump -U $DB_USER -d $DB_NAME -F c > "$BACKUP_DIR/odoo_db_${DATE}.dump"

if [ $? -eq 0 ]; then
    log "✅ Base de datos respaldada: odoo_db_${DATE}.dump"
else
    error "❌ Falló el backup de la base de datos"
    exit 1
fi

# 2. Backup de addons (desde la nueva ruta)
log "📚 Backup de addons..."
if [ -d "$BASE_DIR/data/addons" ]; then
    tar -czf "$BACKUP_DIR/odoo_addons_${DATE}.tar.gz" -C "$BASE_DIR/data/addons" . 2>/dev/null
    log "✅ Addons respaldados desde: $BASE_DIR/data/addons"
else
    warn "⚠️ No se encontró la carpeta de addons en: $BASE_DIR/data/addons"
fi

# 3. Backup de filestore (documentos adjuntos)
log "📎 Backup de filestore..."
if [ -d "$BASE_DIR/data/filestore" ]; then
    tar -czf "$BACKUP_DIR/odoo_filestore_${DATE}.tar.gz" -C "$BASE_DIR/data/filestore" . 2>/dev/null
    log "✅ Filestore respaldado desde: $BASE_DIR/data/filestore"
else
    warn "⚠️ No se encontró la carpeta de filestore en: $BASE_DIR/data/filestore"
fi

# 4. Backup de configuración
log "⚙️ Backup de configuración..."
if [ -f "$BASE_DIR/conf/odoo.cfg" ]; then
    cp "$BASE_DIR/conf/odoo.cfg" "$BACKUP_DIR/odoo_config_${DATE}.cfg"
    log "✅ Configuración respaldada desde: $BASE_DIR/conf/odoo.cfg"
else
    warn "⚠️ No se encontró el archivo de configuración en: $BASE_DIR/conf/odoo.cfg"
fi

# 5. Backup del script de backup (opcional, para tenerlo guardado)
log "📜 Backup del script actual..."
cp "$0" "$BACKUP_DIR/backup_script_${DATE}.sh"
log "✅ Script respaldado"

# 6. Limpiar backups antiguos
log "🧹 Eliminando backups con más de $RETENTION_DAYS días..."
find $BACKUP_BASE_DIR -type d -name "backup_*" -mtime +$RETENTION_DAYS -exec rm -rf {} \; 2>/dev/null || true

log "✅ BACKUP COMPLETADO"
log "📁 Ubicación: $BACKUP_DIR"
log "📊 Tamaño del backup:"
du -sh $BACKUP_DIR

# Mostrar archivos generados
log ""
log "📋 Archivos generados:"
ls -lh $BACKUP_DIR/