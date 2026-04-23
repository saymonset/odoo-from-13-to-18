#!/bin/bash
set -e

# Configuración - Usando rutas ABSOLUTAS
BASE_DIR="$HOME/odoo-from-13-to-18/arquitectura/odoo19"
BACKUP_BASE_DIR="$BASE_DIR/backup/out"
DB_CONTAINER="odoo-db19-n8n"

usage() {
    echo "Uso: $0 <cliente> [nombre_directorio_backup_opcional]"
    echo ""
    echo "Clientes disponibles:"
    ls -1 "$BASE_DIR/clientes/" | sed 's/^/  - /'
    exit 1
}

# Función para expandir rutas (maneja ~ y $HOME)
expand_path() {
    local path="$1"
    local expanded=""
    
    if [ -z "$path" ]; then
        echo ""
        return
    fi
    
    if [[ "$path" == *"\$HOME"* ]]; then
        expanded="${path//\$HOME/$HOME}"
    else
        expanded="$path"
    fi
    
    if [[ "$expanded" == "~"* ]]; then
        expanded="${expanded/#\~/$HOME}"
    fi
    
    expanded=$(echo "$expanded" | cut -d',' -f1 | xargs | tr -d '\r\n')
    
    if [ -z "$expanded" ]; then
        expanded="$CLIENT_DIR/data"
    fi
    
    echo "$expanded"
}

CLIENT_NAME="${1:-}"

if [ -z "$CLIENT_NAME" ]; then
    usage
fi

CLIENT_DIR="$BASE_DIR/clientes/$CLIENT_NAME"

if [ ! -d "$CLIENT_DIR" ]; then
    echo "[ERROR] Cliente no encontrado: $CLIENT_NAME"
    usage
fi

ODOO_CONF="$CLIENT_DIR/conf/odoo.cfg"

if [ ! -d "$BACKUP_BASE_DIR" ]; then
    echo "[ERROR] No existe el directorio: $BACKUP_BASE_DIR"
    exit 1
fi

if [ -n "${2:-}" ]; then
    BACKUP_DIR="$BACKUP_BASE_DIR/$2"
    if [ ! -d "$BACKUP_DIR" ]; then
        echo "[ERROR] El backup especificado no existe: $BACKUP_DIR"
        exit 1
    fi
    echo "[INFO] Backup manual seleccionado: $(basename "$BACKUP_DIR")"
else
    echo "[INFO] Buscando el backup más reciente para el cliente '$CLIENT_NAME'..."
    FOUND_BACKUP=""
    
    for b in $(ls -td "$BACKUP_BASE_DIR"/backup_* 2>/dev/null); do
        if [ -f "$b/backup_info.txt" ]; then
            if grep -q "Cliente: $CLIENT_NAME" "$b/backup_info.txt"; then
                FOUND_BACKUP="$b"
                break
            fi
        fi
    done

    if [ -n "$FOUND_BACKUP" ]; then
        BACKUP_DIR="$FOUND_BACKUP"
        echo "[INFO] Backup encontrado: $(basename "$BACKUP_DIR")"
    else
        echo "[ERROR] No hay backups disponibles para el cliente '$CLIENT_NAME' en $BACKUP_BASE_DIR"
        exit 1
    fi
fi

if [ -f "$ODOO_CONF" ]; then
    DB_NAME=$(grep -E '^db_name\s*=' "$ODOO_CONF" | awk -F '=' '{print $2}' | tr -d ' ' | tr -d '\r')
    DB_USER=$(grep -E '^db_user\s*=' "$ODOO_CONF" | awk -F '=' '{print $2}' | tr -d ' ' | tr -d '\r')
    DB_PASSWORD=$(grep -E '^db_password\s*=' "$ODOO_CONF" | awk -F '=' '{print $2}' | tr -d ' ' | tr -d '\r')
    RAW_DATA_DIR=$(grep -E '^data_dir\s*=' "$ODOO_CONF" | awk -F '=' '{print $2}' | tr -d ' ' | tr -d '\r')
    DATA_DIR=$(expand_path "$RAW_DATA_DIR")
else
    DATA_DIR=""
fi

DB_NAME=${DB_NAME:-dbintegraia_19}
DB_USER=${DB_USER:-integraia_19}
if [ -z "$DATA_DIR" ]; then
    DATA_DIR="$CLIENT_DIR/data"
fi

BACKUP_DATE=$(basename "$BACKUP_DIR" | sed 's/backup_//')
DB_DUMP="$BACKUP_DIR/odoo_db_${BACKUP_DATE}.dump"
ADDONS_TAR="$BACKUP_DIR/odoo_addons_${BACKUP_DATE}.tar.gz"
FILESTORE_TAR="$BACKUP_DIR/odoo_filestore_${BACKUP_DATE}.tar.gz"

if [ ! -f "$DB_DUMP" ]; then
    DB_DUMP="$BACKUP_DIR/dbodoo19_${BACKUP_DATE}.dump"
fi
COMBINED_DATA_TAR="$BACKUP_DIR/odoo_data_${BACKUP_DATE}.tar.gz"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[INFO]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
info() { echo -e "${BLUE}[DEBUG]${NC} $1"; }

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

log "Deteniendo Odoo para $CLIENT_NAME..."
pkill -f "odoo-bin.*--conf $ODOO_CONF" 2>/dev/null || warn "No se encontró proceso Odoo corriendo"
sleep 3

log "Creando directorios necesarios..."
mkdir -p "$DATA_DIR"/{filestore,addons}
mkdir -p "$DATA_DIR/addons"/{oca,extra,enterprise}

if [ ! -d "$DATA_DIR/filestore" ]; then
    error "No se pudo crear el directorio: $DATA_DIR/filestore"
fi

# Restaurar addons
if [ -f "$ADDONS_TAR" ] || [ -f "$COMBINED_DATA_TAR" ]; then
    if [ -f "$ADDONS_TAR" ]; then
        log "Restaurando addons desde: $(basename "$ADDONS_TAR")"
        ACTIVE_TAR="$ADDONS_TAR"
    else
        log "Restaurando addons desde backup combinado: $(basename "$COMBINED_DATA_TAR")"
        ACTIVE_TAR="$COMBINED_DATA_TAR"
    fi
    
    TEMP_ADDONS_DIR="/tmp/restore_addons_$$"
    mkdir -p "$TEMP_ADDONS_DIR"
    
    tar --no-same-owner --no-same-permissions -xzf "$ACTIVE_TAR" -C "$TEMP_ADDONS_DIR"
    
    log "Buscando y clasificando addons..."
    
    while IFS= read -r manifest; do
        module_dir=$(dirname "$manifest")
        module_name=$(basename "$module_dir")
        
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
    warn "No se encontró backup de addons"
fi

# ==============================================================================
# RESTAURAR FILESTORE - CORREGIDO PARA ESTRUCTURA REAL
# ==============================================================================
if [ -f "$FILESTORE_TAR" ] || [ -f "$COMBINED_DATA_TAR" ]; then
    if [ -f "$FILESTORE_TAR" ]; then
        log "Restaurando filestore desde: $(basename "$FILESTORE_TAR")"
        ACTIVE_TAR="$FILESTORE_TAR"
    else
        log "Restaurando filestore desde backup combinado: $(basename "$COMBINED_DATA_TAR")"
        ACTIVE_TAR="$COMBINED_DATA_TAR"
    fi
    
    TEMP_FILESTORE_DIR="/tmp/restore_filestore_$$"
    mkdir -p "$TEMP_FILESTORE_DIR"
    
    log "Extrayendo backup para filestore..."
    tar --no-same-owner --no-same-permissions -xzf "$ACTIVE_TAR" -C "$TEMP_FILESTORE_DIR"
    
    # Depuración: mostrar estructura
    log "Estructura del backup extraído:"
    ls -la "$TEMP_FILESTORE_DIR" | head -10
    
    # Buscar la estructura correcta: filestore/NOMBRE_DB_ORIGINAL/
    # Según tu lista de archivos, la estructura es: ./filestore/dbodoo19/
    
    ORIGINAL_DB_NAME=""
    FILESTORE_SOURCE=""
    
    # Verificar si existe el directorio filestore
    if [ -d "$TEMP_FILESTORE_DIR/filestore" ]; then
        log "Directorio filestore encontrado"
        
        # Buscar subdirectorios dentro de filestore (debería ser dbodoo19)
        for subdir in "$TEMP_FILESTORE_DIR/filestore"/*; do
            if [ -d "$subdir" ]; then
                # Verificar que este subdirectorio contiene la estructura de dos niveles (6e/, e1/, etc.)
                if [ -d "$subdir/6e" ] || [ -d "$subdir/e1" ] || [ -d "$subdir/4b" ]; then
                    ORIGINAL_DB_NAME=$(basename "$subdir")
                    FILESTORE_SOURCE="$subdir"
                    log "✅ Encontrada estructura correcta: filestore/$ORIGINAL_DB_NAME/"
                    break
                fi
            fi
        done
        
        # Si no encontramos por la estructura de dos niveles, tomar el primer subdirectorio
        if [ -z "$FILESTORE_SOURCE" ]; then
            FIRST_SUBDIR=$(find "$TEMP_FILESTORE_DIR/filestore" -maxdepth 1 -type d ! -path "$TEMP_FILESTORE_DIR/filestore" | head -1)
            if [ -n "$FIRST_SUBDIR" ]; then
                ORIGINAL_DB_NAME=$(basename "$FIRST_SUBDIR")
                FILESTORE_SOURCE="$FIRST_SUBDIR"
                log "Usando primer subdirectorio encontrado: $ORIGINAL_DB_NAME"
            fi
        fi
    fi
    
    # Si encontramos el filestore, proceder a restaurar
    if [ -n "$FILESTORE_SOURCE" ] && [ -d "$FILESTORE_SOURCE" ]; then
        log "Filestore original detectado: $ORIGINAL_DB_NAME"
        log "Renombrando a: $DB_NAME"
        
        # Mostrar algunos archivos de ejemplo para confirmar
        log "Ejemplo de archivos en el filestore original:"
        find "$FILESTORE_SOURCE" -type f | head -5
        
        # Limpiar destino si existe
        rm -rf "$DATA_DIR/filestore/$DB_NAME"
        mkdir -p "$DATA_DIR/filestore"
        
        # Copiar el contenido completo del filestore
        log "Copiando archivos desde: $FILESTORE_SOURCE"
        cp -r "$FILESTORE_SOURCE" "$DATA_DIR/filestore/$DB_NAME"
        
        # Contar archivos restaurados
        FILE_COUNT=$(find "$DATA_DIR/filestore/$DB_NAME" -type f | wc -l)
        log "✅ Filestore restaurado en $DATA_DIR/filestore/$DB_NAME"
        log "📁 Archivos restaurados: $FILE_COUNT"
        
        # Verificar estructura de dos niveles
        if [ -d "$DATA_DIR/filestore/$DB_NAME/6e" ]; then
            log "✅ Estructura correcta detectada (subdirectorios de dos letras)"
            log "   Ejemplo: $(ls "$DATA_DIR/filestore/$DB_NAME/6e" | head -3)"
        fi
    else
        warn "No se encontró el directorio filestore en el backup"
        log "Buscando en toda la estructura extraída:"
        find "$TEMP_FILESTORE_DIR" -type d | head -30
    fi
    
    rm -rf "$TEMP_FILESTORE_DIR"
else
    warn "No se encontró backup de filestore"
fi

log "Ajustando permisos..."
chown -R $(whoami):$(whoami) "$DATA_DIR" 2>/dev/null || true
chmod -R 755 "$DATA_DIR" 2>/dev/null || true

# Crear/verificar rol en PostgreSQL
log "Verificando rol '$DB_USER' en PostgreSQL..."

ROLE_EXISTS=$(docker exec $DB_CONTAINER psql -U odoo -d postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" 2>/dev/null || echo "0")

if [ "$ROLE_EXISTS" = "1" ]; then
    log "✅ El rol '$DB_USER' ya existe"
    docker exec $DB_CONTAINER psql -U odoo -d postgres -c "ALTER ROLE \"$DB_USER\" WITH LOGIN PASSWORD '$DB_PASSWORD';" 2>/dev/null || true
else
    log "Creando rol '$DB_USER'..."
    docker exec $DB_CONTAINER psql -U odoo -d postgres -c "CREATE ROLE \"$DB_USER\" WITH LOGIN PASSWORD '$DB_PASSWORD' CREATEDB;" 2>/dev/null || true
    log "✅ Rol '$DB_USER' creado"
fi

# Restaurar base de datos
log "Restaurando base de datos $DB_NAME..."

docker exec $DB_CONTAINER psql -U odoo -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='$DB_NAME';" 2>/dev/null || true
docker exec $DB_CONTAINER dropdb -U odoo --if-exists $DB_NAME 2>/dev/null || true
docker exec $DB_CONTAINER createdb -U odoo -O "$DB_USER" $DB_NAME

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

echo ""
log "=========================================="
log "✅ RESTAURACIÓN COMPLETADA"
log "=========================================="
log "Base de datos: $DB_NAME"
log "Usuario DB: $DB_USER"
log "Data directory: $DATA_DIR"
log "Filestore: $DATA_DIR/filestore/$DB_NAME"
log "Addons OCA: $DATA_DIR/addons/oca"
log "Addons EXTRA: $DATA_DIR/addons/extra"
log "Addons ENTERPRISE: $DATA_DIR/addons/enterprise"
log "Puerto Odoo: $(grep '^http_port' $ODOO_CONF | awk -F '=' '{print $2}' | tr -d ' ')"
log ""
log "Para iniciar Odoo:"
echo "  cd $BASE_DIR/odoo/odoo"
echo "  python3 odoo-bin -c $ODOO_CONF"