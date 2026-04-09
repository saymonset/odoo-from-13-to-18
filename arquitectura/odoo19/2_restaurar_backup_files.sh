#!/bin/bash

# Script para restaurar BD y filestore desde backup
# Uso: ./2_restaurar_backup_files.sh NOMBRE_BD USUARIO PASSWORD RUTA_SQL RUTA_FILESTORE_ORIGEN

# Ejemplo:
# ./2_restaurar_backup_files.sh dbintegraia_19 integraia_19 Admin123 \
#     "/home/simon/opt/odoo/odoo-from-13-to-18/backup_integradev-2026-03-18/backup_bd/db.sql" \
#     "/home/simon/opt/odoo/odoo-from-13-to-18/backup_integradev-2026-03-18/data/filestore/dbintegraiadev"

NOMBRE_BD="$1"
USUARIO="$2"
PASSWORD="$3"
RUTA_SQL="$4"
RUTA_FILESTORE_ORIGEN="$5"

CONTAINER_DB="odoo-db19-n8n"
DB_ADMIN="odoo"
DESTINO="/home/simon/opt/odoo"
RUTA_FILESTORE_DESTINO="${DESTINO}/odoo-from-13-to-18/arquitectura/odoo19/clientes/${USUARIO}/data/filestore/${NOMBRE_BD}"

# Verificar parámetros mínimos
if [ -z "$NOMBRE_BD" ] || [ -z "$USUARIO" ] || [ -z "$PASSWORD" ] || [ -z "$RUTA_SQL" ] || [ -z "$RUTA_FILESTORE_ORIGEN" ]; then
    echo "❌ Uso: $0 NOMBRE_BD USUARIO PASSWORD RUTA_SQL RUTA_FILESTORE_ORIGEN"
    echo ""
    echo "Ejemplo:"
    echo "  $0 dbintegraia_19 integraia_19 Admin123 \\"
    echo '    "${DESTINO}/odoo-from-13-to-18/backup_integradev-2026-03-18/backup_bd/db.sql" \\'
    echo '    "${DESTINO}/odoo-from-13-to-18/backup_integradev-2026-03-18/data/filestore/dbintegraiadev"'
    exit 1
fi

# Verificar que los archivos existan
if [ ! -f "$RUTA_SQL" ]; then
    echo "❌ Archivo SQL no encontrado: $RUTA_SQL"
    exit 1
fi

if [ ! -d "$RUTA_FILESTORE_ORIGEN" ]; then
    echo "❌ Carpeta filestore origen no encontrada: $RUTA_FILESTORE_ORIGEN"
    exit 1
fi

echo "=========================================="
echo "🔄 Restaurando backup a: $NOMBRE_BD"
echo "=========================================="
echo "📂 SQL origen: $RUTA_SQL"
echo "📂 Filestore origen: $RUTA_FILESTORE_ORIGEN"
echo "📂 Filestore destino: $RUTA_FILESTORE_DESTINO"
echo ""

# 1. Verificar contenedor
echo "📦 Verificando contenedor..."
if ! docker ps | grep -q $CONTAINER_DB; then
    echo "❌ Contenedor $CONTAINER_DB no está corriendo"
    exit 1
fi
echo "✅ Contenedor encontrado"

# 2. Eliminar BD destino si existe
echo "🗑️  Eliminando base destino si existe..."
docker exec $CONTAINER_DB psql -U $DB_ADMIN -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='$NOMBRE_BD';" 2>/dev/null
docker exec $CONTAINER_DB dropdb -U $DB_ADMIN $NOMBRE_BD 2>/dev/null
echo "✅ Listo"

# 3. Crear BD destino
echo "🆕 Creando base $NOMBRE_BD..."
docker exec $CONTAINER_DB createdb -U $DB_ADMIN $NOMBRE_BD
echo "✅ Base creada"

# 4. Copiar SQL al contenedor
echo "📁 Copiando archivo SQL al contenedor..."
docker cp "$RUTA_SQL" $CONTAINER_DB:/tmp/restore.sql
echo "✅ Copiado"

# 5. Restaurar SQL
echo "💾 Restaurando datos desde SQL..."
docker exec $CONTAINER_DB psql -U $DB_ADMIN -d $NOMBRE_BD -f /tmp/restore.sql
if [ $? -eq 0 ]; then
    echo "✅ Datos restaurados correctamente"
else
    echo "⚠️  Posibles errores durante la restauración (pueden ser normales)"
fi

# 6. Limpiar archivo SQL del contenedor
echo "🧹 Limpiando archivos temporales..."
docker exec $CONTAINER_DB rm /tmp/restore.sql
echo "✅ Limpio"

# 7. Copiar filestore
echo "=========================================="
echo "📁 Copiando filestore..."
echo "   Desde: $RUTA_FILESTORE_ORIGEN"
echo "   Hacia: $RUTA_FILESTORE_DESTINO"

# Crear directorio destino
mkdir -p "$RUTA_FILESTORE_DESTINO"

# Copiar archivos
if command -v rsync &> /dev/null; then
    rsync -av --progress "$RUTA_FILESTORE_ORIGEN/" "$RUTA_FILESTORE_DESTINO/"
else
    cp -r "$RUTA_FILESTORE_ORIGEN/"* "$RUTA_FILESTORE_DESTINO/"
fi

echo "✅ Filestore copiado"

# Mostrar resumen
FILE_COUNT=$(find "$RUTA_FILESTORE_DESTINO" -type f | wc -l)
DIR_SIZE=$(du -sh "$RUTA_FILESTORE_DESTINO" | cut -f1)
echo "   Archivos: $FILE_COUNT"
echo "   Tamaño: $DIR_SIZE"

# 8. Crear/actualizar usuario
echo "👤 Configurando usuario $USUARIO..."
USER_EXISTS=$(docker exec $CONTAINER_DB psql -U $DB_ADMIN -d postgres -t -c "SELECT 1 FROM pg_roles WHERE rolname='$USUARIO';" | xargs)
if [ "$USER_EXISTS" != "1" ]; then
    docker exec $CONTAINER_DB psql -U $DB_ADMIN -d postgres -c "CREATE USER $USUARIO WITH PASSWORD '$PASSWORD';"
    echo "✅ Usuario creado"
else
    docker exec $CONTAINER_DB psql -U $DB_ADMIN -d postgres -c "ALTER USER $USUARIO WITH PASSWORD '$PASSWORD';"
    echo "✅ Usuario actualizado"
fi

# 9. Otorgar permisos
echo "🔐 Otorgando permisos..."
docker exec $CONTAINER_DB psql -U $DB_ADMIN -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE $NOMBRE_BD TO $USUARIO;"
docker exec $CONTAINER_DB psql -U $DB_ADMIN -d $NOMBRE_BD -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $USUARIO;"
docker exec $CONTAINER_DB psql -U $DB_ADMIN -d $NOMBRE_BD -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $USUARIO;"
docker exec $CONTAINER_DB psql -U $DB_ADMIN -d $NOMBRE_BD -c "ALTER SCHEMA public OWNER TO $USUARIO;"
docker exec $CONTAINER_DB psql -U $DB_ADMIN -d postgres -c "ALTER DATABASE $NOMBRE_BD OWNER TO $USUARIO;"
echo "✅ Permisos otorgados"

# 10. Verificar
echo "📊 Verificando restauración..."
TABLAS=$(docker exec $CONTAINER_DB psql -U $DB_ADMIN -d $NOMBRE_BD -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';" | xargs)
echo "✅ $TABLAS tablas restauradas"

# Verificar si hay datos en ir.attachment
ATTACHMENTS=$(docker exec $CONTAINER_DB psql -U $DB_ADMIN -d $NOMBRE_BD -t -c "SELECT COUNT(*) FROM ir_attachment;" 2>/dev/null | xargs)
if [ -n "$ATTACHMENTS" ]; then
    echo "📎 $ATTACHMENTS attachments en la base de datos"
fi

echo "=========================================="
echo "✅ ¡Restauración completada!"
echo "=========================================="
echo "📋 Datos de conexión:"
echo "   Base: $NOMBRE_BD"
echo "   Usuario: $USUARIO"
echo "   Password: $PASSWORD"
echo "   Filestore: $RUTA_FILESTORE_DESTINO"
echo ""
echo "🔧 Para usar en Odoo, actualiza tu odoo.cfg:"
echo "   db_name = $NOMBRE_BD"
echo "   db_user = $USUARIO"
echo "   db_password = $PASSWORD"
echo "   data_dir = $(dirname "$RUTA_FILESTORE_DESTINO")"
echo "=========================================="