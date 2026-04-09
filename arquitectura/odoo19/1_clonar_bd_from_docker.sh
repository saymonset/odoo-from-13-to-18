#!/bin/bash

# Script para clonar BD Y filestore
# Uso: ./clonar_bd.sh ORIGEN DESTINO USUARIO PASSWORD [RUTA_FILESTORE_ORIGEN] [RUTA_FILESTORE_DESTINO]

# Solo clonar BD (sin filestore)
# ./clonar_bd.sh dbhoteljumpjibe_19 dbintegraia_19

# BD + usuario específico
# ./clonar_bd.sh dbhoteljumpjibe_19 dbintegraia_19 integraia_19 password

# BD + Filestore completo
# ./clonar_bd.sh dbhoteljumpjibe_19 dbintegraia_19 integraia_19 Admin123 \
#     "/home/simon/opt/odoo/odoo-from-13-to-18/arquitectura/odoo19/clientes/hoteljumpjibe_19/data/filestore/dbhoteljumpjibe_19" \
#     "/home/simon/opt/odoo/odoo-from-13-to-18/arquitectura/odoo19/clientes/integraia_19/data/filestore/dbintegraia_19"

ORIGEN="$1"
DESTINO="$2"
USUARIO="$3"
PASSWORD="$4"
FILESTORE_ORIGEN="$5"
FILESTORE_DESTINO="$6"

CONTAINER_DB="odoo-db19-n8n"
DB_ADMIN="odoo"

# Verificar parámetros mínimos
if [ -z "$ORIGEN" ] || [ -z "$DESTINO" ]; then
    echo "❌ Uso: $0 ORIGEN DESTINO [USUARIO] [PASSWORD] [RUTA_FILESTORE_ORIGEN] [RUTA_FILESTORE_DESTINO]"
    echo ""
    echo "Ejemplo mínimo (solo BD):"
    echo "  $0 dbhoteljumpjibe_19 dbintegraia_19"
    echo ""
    echo "Ejemplo completo (BD + Filestore):"
    echo "  $0 dbhoteljumpjibe_19 dbintegraia_19 integraia_19 password /home/simon/opt/odoo/odoo-from-13-to-18/arquitectura/odoo19/clientes/hoteljumpjibe_19/data/filestore/dbhoteljumpjibe_19 /home/simon/opt/odoo/odoo-from-13-to-18/arquitectura/odoo19/clientes/integraia_19/data/filestore/dbintegraia_19"
    exit 1
fi

# Valores por defecto
USUARIO="${USUARIO:-$DESTINO}"
PASSWORD="${PASSWORD:-${USUARIO}_2024}"

echo "=========================================="
echo "🔄 Clonando: $ORIGEN → $DESTINO"
echo "=========================================="
echo "📂 Filestore origen: ${FILESTORE_ORIGEN:-'No especificado (solo BD)'}"
echo "📂 Filestore destino: ${FILESTORE_DESTINO:-'No especificado (solo BD)'}"
echo ""

# 1. Verificar contenedor
echo "📦 Verificando contenedor..."
if ! docker ps | grep -q $CONTAINER_DB; then
    echo "❌ Contenedor $CONTAINER_DB no está corriendo"
    exit 1
fi
echo "✅ Contenedor encontrado"

# 2. Eliminar BD destino si existe
echo "🗑️  Preparando base destino..."
docker exec $CONTAINER_DB psql -U $DB_ADMIN -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='$DESTINO';" 2>/dev/null
docker exec $CONTAINER_DB dropdb -U $DB_ADMIN $DESTINO 2>/dev/null
echo "✅ Listo"

# 3. Crear backup
echo "📦 Creando backup de $ORIGEN..."
docker exec $CONTAINER_DB pg_dump -U $DB_ADMIN -F c $ORIGEN > /tmp/${ORIGEN}.dump
echo "✅ Backup creado"

# 4. Copiar al contenedor
echo "📁 Copiando backup..."
docker cp /tmp/${ORIGEN}.dump $CONTAINER_DB:/tmp/backup.dump
echo "✅ Copiado"

# 5. Crear BD destino
echo "🆕 Creando $DESTINO..."
docker exec $CONTAINER_DB createdb -U $DB_ADMIN $DESTINO
echo "✅ Base creada"

# 6. Restaurar
echo "💾 Restaurando datos..."
docker exec $CONTAINER_DB pg_restore -U $DB_ADMIN -d $DESTINO -c --no-owner /tmp/backup.dump
echo "✅ Datos restaurados"

# 7. Limpiar
echo "🧹 Limpiando..."
docker exec $CONTAINER_DB rm /tmp/backup.dump
rm /tmp/${ORIGEN}.dump
echo "✅ Limpio"

# 8. Copiar filestore si se especificaron rutas
if [ -n "$FILESTORE_ORIGEN" ] && [ -n "$FILESTORE_DESTINO" ]; then
    if [ -d "$FILESTORE_ORIGEN" ]; then
        echo "=========================================="
        echo "📁 Copiando filestore..."
        echo "   Desde: $FILESTORE_ORIGEN"
        echo "   Hacia: $FILESTORE_DESTINO"
        
        # Crear directorio destino
        mkdir -p "$FILESTORE_DESTINO"
        
        # Copiar archivos
        if command -v rsync &> /dev/null; then
            rsync -av --progress "$FILESTORE_ORIGEN/" "$FILESTORE_DESTINO/"
        else
            cp -r "$FILESTORE_ORIGEN/"* "$FILESTORE_DESTINO/"
        fi
        
        echo "✅ Filestore copiado"
        
        # Mostrar resumen
        FILE_COUNT=$(find "$FILESTORE_DESTINO" -type f | wc -l)
        DIR_SIZE=$(du -sh "$FILESTORE_DESTINO" | cut -f1)
        echo "   Archivos: $FILE_COUNT"
        echo "   Tamaño: $DIR_SIZE"
    else
        echo "⚠️  Filestore origen no existe: $FILESTORE_ORIGEN"
    fi
else
    echo "⏭️  Omitiendo copia de filestore (no se especificaron rutas)"
fi

# 9. Crear usuario si no existe
echo "👤 Configurando usuario $USUARIO..."
USER_EXISTS=$(docker exec $CONTAINER_DB psql -U $DB_ADMIN -d postgres -t -c "SELECT 1 FROM pg_roles WHERE rolname='$USUARIO';" | xargs)
if [ "$USER_EXISTS" != "1" ]; then
    docker exec $CONTAINER_DB psql -U $DB_ADMIN -d postgres -c "CREATE USER $USUARIO WITH PASSWORD '$PASSWORD';"
else
    docker exec $CONTAINER_DB psql -U $DB_ADMIN -d postgres -c "ALTER USER $USUARIO WITH PASSWORD '$PASSWORD';"
fi
echo "✅ Usuario configurado"

# 10. Otorgar permisos
echo "🔐 Otorgando permisos..."
docker exec $CONTAINER_DB psql -U $DB_ADMIN -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DESTINO TO $USUARIO;"
docker exec $CONTAINER_DB psql -U $DB_ADMIN -d $DESTINO -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $USUARIO;"
docker exec $CONTAINER_DB psql -U $DB_ADMIN -d $DESTINO -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $USUARIO;"
docker exec $CONTAINER_DB psql -U $DB_ADMIN -d $DESTINO -c "ALTER SCHEMA public OWNER TO $USUARIO;"
docker exec $CONTAINER_DB psql -U $DB_ADMIN -d postgres -c "ALTER DATABASE $DESTINO OWNER TO $USUARIO;"
echo "✅ Permisos otorgados"

# 11. Verificar
echo "📊 Verificando..."
TABLAS=$(docker exec $CONTAINER_DB psql -U $DB_ADMIN -d $DESTINO -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';" | xargs)
echo "✅ $TABLAS tablas restauradas"

echo "=========================================="
echo "✅ ¡Clonación completada!"
echo "=========================================="
echo "📋 Datos de conexión:"
echo "   Base: $DESTINO"
echo "   Usuario: $USUARIO"
echo "   Password: $PASSWORD"
if [ -n "$FILESTORE_DESTINO" ]; then
    echo "   Filestore: $FILESTORE_DESTINO"
fi
echo ""
echo "🔧 Para usar en Odoo, actualiza tu odoo.cfg:"
echo "   db_name = $DESTINO"
echo "   db_user = $USUARIO"
echo "   db_password = $PASSWORD"
if [ -n "$FILESTORE_DESTINO" ]; then
    echo "   data_dir = $(dirname "$FILESTORE_DESTINO")"
fi
echo "=========================================="