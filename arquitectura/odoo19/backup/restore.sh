#!/bin/bash
set -e

# Configuración - Usando Docker para PostgreSQL
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_BASE_DIR="$SCRIPT_DIR/out"
DB_CONTAINER="odoo-db19-n8n"  # Tu contenedor de PostgreSQL
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

# Buscar el backup más reciente automáticamente
if [ -d "$BACKUP_BASE_DIR" ]; then
    LATEST_BACKUP=$(ls -td "$BACKUP_BASE_DIR"/backup_* 2>/dev/null | head -1)
    if [ -n "$LATEST_BACKUP" ]; then
        BACKUP_DIR="$LATEST_BACKUP"
    else
        BACKUP_DIR="$BACKUP_BASE_DIR"
    fi
else
    BACKUP_DIR="$BACKUP_BASE_DIR"
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

# Función para crear/verificar el rol en PostgreSQL usando superuser 'odoo'
ensure_role() {
    local role=$1
    local password=$2
    
    info "Verificando/Creando rol '$role' en PostgreSQL usando superuser '$SUPERUSER'..."
    
    # Verificar si podemos conectar como superuser
    if ! docker exec $DB_CONTAINER psql -U $SUPERUSER -d postgres -c "SELECT 1" &>/dev/null; then
        error "No se puede conectar como superuser '$SUPERUSER'. Verifica que el contenedor esté funcionando."
    fi
    
    # Verificar si el rol existe
    if docker exec $DB_CONTAINER psql -U $SUPERUSER -d postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='$role'" | grep -q 1; then
        info "El rol '$role' ya existe, actualizando contraseña..."
        docker exec $DB_CONTAINER psql -U $SUPERUSER -d postgres -c "ALTER ROLE \"$role\" WITH LOGIN PASSWORD '$password';"
    else
        info "Creando rol '$role'..."
        docker exec $DB_CONTAINER psql -U $SUPERUSER -d postgres -c "CREATE ROLE \"$role\" WITH LOGIN PASSWORD '$password' CREATEDB;"
    fi
    
    # Asegurar que tenga permisos CREATEDB
    docker exec $DB_CONTAINER psql -U $SUPERUSER -d postgres -c "ALTER ROLE \"$role\" WITH CREATEDB;"
    
    # Otorgar permisos en la base de datos postgres (para crear bases de datos)
    docker exec $DB_CONTAINER psql -U $SUPERUSER -d postgres -c "GRANT CONNECT ON DATABASE postgres TO \"$role\";" 2>/dev/null || true
    
    log "✅ Rol '$role' configurado correctamente"
}

usage() {
    echo "Uso: $0 [cliente] [opciones]"
    echo ""
    echo "Clientes disponibles:"
    ls -1 "$HOME/opt/odoo/odoo-from-13-to-18/arquitectura/odoo19/clientes/" | sed 's/^/  - /'
    echo ""
    echo "Opciones:"
    echo "  -l, --list        Listar backups disponibles"
    echo "  -f, --file FILE   Restaurar desde archivo específico"
    echo "  --install-modules Instalar módulos OCA después de restaurar"
    echo "  --create-role     Solo crear/verificar el rol en PostgreSQL"
    echo "  -h, --help        Mostrar ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0 integraia_19                    # Restaurar último backup para integraia_19"
    echo "  $0 hoteljumpjibe_19 --install-modules  # Restaurar e instalar módulos"
    echo "  $0 --list                          # Listar todos los backups"
    echo "  $0 integraia_19 --create-role      # Solo crear el rol"
    exit 0
}

list_backups() {
    echo "=========================================="
    echo "📚 Backups disponibles en: $BACKUP_BASE_DIR"
    echo "=========================================="
    
    for backup in $(ls -td "$BACKUP_BASE_DIR"/backup_* 2>/dev/null); do
        echo ""
        echo "📁 $(basename "$backup")"
        echo "   🗄️ Bases de datos:"
        ls -lh "$backup"/odoo_db_*.dump 2>/dev/null | awk '{print "      - " $9 " (" $5 ")"}' || echo "      No hay backups"
        echo "   📎 Filestore+Addons:"
        ls -lh "$backup"/odoo_filestore_*.tar.gz 2>/dev/null | awk '{print "      - " $9 " (" $5 ")"}' || echo "      No hay backups"
    done
}

restore() {
    local dump_file=$1
    local INSTALL_MODULES=${2:-false}
    local ORIGINAL_DB_NAME=""
    
    if [ ! -f "$dump_file" ]; then
        error "Archivo no encontrado: $dump_file"
        exit 1
    fi
    
    local BASE_NAME=$(basename "$dump_file" | sed 's/odoo_db_//' | sed 's/\.dump//')
    local FILESTORE_FILE="$(dirname "$dump_file")/odoo_filestore_${BASE_NAME}.tar.gz"
    
    info "=========================================="
    info "Restaurando cliente: $CLIENT_NAME"
    info "Base de datos destino: $DB_NAME"
    info "Usuario DB: $DB_USER"
    info "Data directory: $DATA_DIR"
    info "Backup: $BASE_NAME"
    info "=========================================="
    
    # 1. Asegurar que el rol existe
    ensure_role "$DB_USER" "$DB_PASSWORD"
    
    # 2. Detener Odoo (si está corriendo como servicio)
    info "Deteniendo servicio Odoo para $CLIENT_NAME..."
    pkill -f "odoo-bin.*--conf $ODOO_CONF" 2>/dev/null || warn "No se encontró proceso Odoo corriendo"
    sleep 3
    
    # 3. Restaurar filestore y addons
    if [ -f "$FILESTORE_FILE" ]; then
        info "Restaurando filestore y addons..."
        
        local TEMP_RESTORE_DIR="/tmp/restore_$$"
        mkdir -p "$TEMP_RESTORE_DIR"
        
        # Extraer todo el contenido
        tar --no-same-owner --no-same-permissions -xzf "$FILESTORE_FILE" -C "$TEMP_RESTORE_DIR"
        
        # Buscar y restaurar filestore
        local FILESTORE_BASE=$(find "$TEMP_RESTORE_DIR" -type d -name "filestore" | head -1)
        
        if [ -n "$FILESTORE_BASE" ]; then
            # Obtener el nombre original de la BD
            ORIGINAL_DB_NAME=$(find "$FILESTORE_BASE" -maxdepth 1 -type d ! -path "$FILESTORE_BASE" | head -1 | xargs basename 2>/dev/null)
            
            if [ -n "$ORIGINAL_DB_NAME" ]; then
                info "Filestore original detectado: $ORIGINAL_DB_NAME"
                info "Renombrando a: $DB_NAME"
                
                # Eliminar filestore existente
                sudo rm -rf "$DATA_DIR/filestore/$DB_NAME"
                mkdir -p "$DATA_DIR/filestore"
                sudo mv "$FILESTORE_BASE/$ORIGINAL_DB_NAME" "$DATA_DIR/filestore/$DB_NAME"
                
                log "✅ Filestore restaurado en $DATA_DIR/filestore/$DB_NAME"
            fi
        fi
        
        # Restaurar addons (extra-addons)
        info "Restaurando addons..."
        
        # Buscar estructura oca y extra
        local OCA_DIR=$(find "$TEMP_RESTORE_DIR" -type d -path "*/oca" | head -1)
        if [ -n "$OCA_DIR" ] && [ "$(ls -A "$OCA_DIR" 2>/dev/null)" ]; then
            info "Restaurando módulos OCA..."
            sudo rm -rf "$CLIENT_DIR/extra-addons/oca"
            sudo mkdir -p "$CLIENT_DIR/extra-addons/oca"
            sudo cp -r "$OCA_DIR"/* "$CLIENT_DIR/extra-addons/oca/"
            log "✅ Módulos OCA restaurados"
        fi
        
        local EXTRA_DIR=$(find "$TEMP_RESTORE_DIR" -type d -path "*/extra" | head -1)
        if [ -n "$EXTRA_DIR" ] && [ "$(ls -A "$EXTRA_DIR" 2>/dev/null)" ]; then
            info "Restaurando módulos EXTRA..."
            sudo rm -rf "$CLIENT_DIR/extra-addons/extra"
            sudo mkdir -p "$CLIENT_DIR/extra-addons/extra"
            sudo cp -r "$EXTRA_DIR"/* "$CLIENT_DIR/extra-addons/extra/"
            log "✅ Módulos EXTRA restaurados"
        fi
        
        # También buscar addons directos
        local ADDONS_DIR=$(find "$TEMP_RESTORE_DIR" -type d -name "addons" ! -path "*/oca/*" ! -path "*/extra/*" | head -1)
        if [ -n "$ADDONS_DIR" ] && [ "$(ls -A "$ADDONS_DIR" 2>/dev/null)" ]; then
            info "Restaurando addons adicionales..."
            sudo cp -r "$ADDONS_DIR"/* "$CLIENT_DIR/extra-addons/" 2>/dev/null || true
            log "✅ Addons adicionales restaurados"
        fi
        
        # Limpiar permisos
        sudo chown -R $(whoami):$(whoami) "$CLIENT_DIR/extra-addons/" 2>/dev/null || true
        sudo chmod -R 755 "$CLIENT_DIR/extra-addons/" 2>/dev/null || true
        sudo chown -R $(whoami):$(whoami) "$DATA_DIR/filestore/" 2>/dev/null || true
        sudo chmod -R 755 "$DATA_DIR/filestore/" 2>/dev/null || true
        
        sudo rm -rf "$TEMP_RESTORE_DIR"
        log "✅ Filestore y addons restaurados"
    else
        warn "No se encontró backup de filestore"
    fi
    
    # 4. Restaurar base de datos usando Docker
    info "Restaurando base de datos $DB_NAME en contenedor $DB_CONTAINER..."
    
    info "Eliminando base de datos existente..."
    docker exec -e PGPASSWORD=$DB_PASSWORD $DB_CONTAINER psql -U $DB_USER -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='$DB_NAME';" 2>/dev/null || true
    docker exec -e PGPASSWORD=$DB_PASSWORD $DB_CONTAINER dropdb -U $DB_USER --if-exists $DB_NAME 2>/dev/null || true
    docker exec -e PGPASSWORD=$DB_PASSWORD $DB_CONTAINER createdb -U $DB_USER $DB_NAME
    
    info "Restaurando dump de base de datos..."
    set +e
    docker exec -i -e PGPASSWORD=$DB_PASSWORD $DB_CONTAINER pg_restore \
        -U $DB_USER \
        -d $DB_NAME \
        --no-owner \
        --no-privileges \
        < "$dump_file" 2>&1
    PG_EXIT=$?
    set -e
    
    if [ $PG_EXIT -eq 0 ]; then
        log "✅ Base de datos restaurada"
        
        if [ -n "$ORIGINAL_DB_NAME" ] && [ "$ORIGINAL_DB_NAME" != "$DB_NAME" ]; then
            info "Actualizando referencias al filestore..."
            docker exec -e PGPASSWORD=$DB_PASSWORD $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c \
                "UPDATE ir_attachment SET store_fname = REPLACE(store_fname, '$ORIGINAL_DB_NAME', '$DB_NAME') WHERE store_fname LIKE '%$ORIGINAL_DB_NAME%';" \
                2>/dev/null || true
        fi
    else
        error "❌ Falló la restauración de la base de datos (código: $PG_EXIT)"
        exit 1
    fi
    
    # 5. Iniciar Odoo nuevamente
    info "Iniciando Odoo para $CLIENT_NAME..."
    warn "Debes iniciar Odoo manualmente para $CLIENT_NAME con:"
    echo "  cd $HOME/opt/odoo/odoo-from-13-to-18/arquitectura/odoo19/odoo/odoo"
    echo "  python3 odoo-bin -c $ODOO_CONF"
    echo ""
    echo "O si usas screen:"
    echo "  screen -dmS odoo-$CLIENT_NAME bash -c 'cd $HOME/opt/odoo/odoo-from-13-to-18/arquitectura/odoo19/odoo/odoo && python3 odoo-bin -c $ODOO_CONF'"
    
    sleep 3
    
    echo ""
    log "✅ RESTAURACIÓN COMPLETADA"
    info "Cliente: $CLIENT_NAME"
    info "Base de datos: $DB_NAME"
    info "Usuario: $DB_USER"
    info "Filestore: $DATA_DIR/filestore/$DB_NAME"
    info "Addons OCA: $CLIENT_DIR/extra-addons/oca"
    info "Addons EXTRA: $CLIENT_DIR/extra-addons/extra"
    info "Puerto Odoo: $(grep '^http_port' $ODOO_CONF | awk -F '=' '{print $2}' | tr -d ' ')"
    info "Accede a Odoo en: http://localhost:$(grep '^http_port' $ODOO_CONF | awk -F '=' '{print $2}' | tr -d ' ')"
}

# Procesar argumentos
# Si el primer argumento no empieza con -, es el nombre del cliente
if [[ $1 && $1 != -* ]]; then
    CLIENT_NAME="$1"
    CLIENT_DIR="$HOME/opt/odoo/odoo-from-13-to-18/arquitectura/odoo19/clientes/$CLIENT_NAME"
    ODOO_CONF="$CLIENT_DIR/conf/odoo.cfg"
    shift  # Remover el cliente de los argumentos
fi

# Extraer variables del config después de posible cambio de cliente
if [ -f "$ODOO_CONF" ]; then
    DB_NAME=$(grep -E '^db_name\s*=' "$ODOO_CONF" | awk -F '=' '{print $2}' | tr -d ' ' | tr -d '\r')
    DB_USER=$(grep -E '^db_user\s*=' "$ODOO_CONF" | awk -F '=' '{print $2}' | tr -d ' ' | tr -d '\r')
    DB_PASSWORD=$(grep -E '^db_password\s*=' "$ODOO_CONF" | awk -F '=' '{print $2}' | tr -d ' ' | tr -d '\r')
    DATA_DIR=$(grep -E '^data_dir\s*=' "$ODOO_CONF" | awk -F '=' '{print $2}' | tr -d ' ' | tr -d '\r')
    DATA_DIR="${DATA_DIR/#\~/$HOME}"
fi

INSTALL_MODULES=false

case $1 in
    -l|--list)
        list_backups
        ;;
    -f|--file)
        if [ "$3" = "--install-modules" ]; then
            INSTALL_MODULES=true
        fi
        restore "$2" "$INSTALL_MODULES"
        ;;
    --install-modules)
        INSTALL_MODULES=true
        LATEST=$(ls -t "$BACKUP_DIR"/odoo_db_*.dump 2>/dev/null | head -1)
        if [ -z "$LATEST" ]; then
            error "No hay backups disponibles"
            exit 1
        fi
        restore "$LATEST" "$INSTALL_MODULES"
        ;;
    --create-role)
        ensure_role "$DB_USER" "$DB_PASSWORD"
        ;;
    -h|--help)
        usage
        ;;
    *)
        LATEST=$(ls -t "$BACKUP_DIR"/odoo_db_*.dump 2>/dev/null | head -1)
        if [ -z "$LATEST" ]; then
            error "No hay backups disponibles en $BACKUP_DIR"
            exit 1
        fi
        restore "$LATEST" false
        ;;
esac