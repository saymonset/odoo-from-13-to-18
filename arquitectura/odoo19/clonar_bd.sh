#!/bin/bash

# Script simplificado para clonar BD
# Uso: ./clonar_bd.sh ORIGEN DESTINO USUARIO PASSWORD
#./clonar_bd.sh dbhoteljumpjibe_19 dbintegraia_19 integraia_19 Admin123
ORIGEN="$1"
DESTINO="$2"
USUARIO="$3"
PASSWORD="$4"
CONTAINER="odoo-db19-n8n"
DB_ADMIN="odoo"

# Verificar parámetros
if [ -z "$ORIGEN" ] || [ -z "$DESTINO" ]; then
    echo "❌ Uso: $0 ORIGEN DESTINO [USUARIO] [PASSWORD]"
    echo "Ejemplo: $0 dbhoteljumpjibe_19 dbintegraia_19 integraia_19 xxxxx"
    exit 1
fi

# Si no especifica usuario, usa el nombre de la BD destino
if [ -z "$USUARIO" ]; then
    USUARIO="$DESTINO"
fi

# Si no especifica password, genera una
if [ -z "$PASSWORD" ]; then
    PASSWORD="${USUARIO}_2024"
fi

echo "=========================================="
echo "🔄 Clonando: $ORIGEN → $DESTINO"
echo "=========================================="

# 1. Verificar contenedor
echo "📦 Verificando contenedor..."
if ! docker ps | grep -q $CONTAINER; then
    echo "❌ Contenedor $CONTAINER no está corriendo"
    exit 1
fi
echo "✅ Contenedor encontrado"

# 2. Eliminar BD destino si existe
echo "🗑️  Preparando base destino..."
docker exec $CONTAINER psql -U $DB_ADMIN -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='$DESTINO';" 2>/dev/null
docker exec $CONTAINER dropdb -U $DB_ADMIN $DESTINO 2>/dev/null
echo "✅ Listo"

# 3. Crear backup
echo "📦 Creando backup de $ORIGEN..."
docker exec $CONTAINER pg_dump -U $DB_ADMIN -F c $ORIGEN > /tmp/${ORIGEN}.dump
echo "✅ Backup creado"

# 4. Copiar al contenedor
echo "📁 Copiando backup..."
docker cp /tmp/${ORIGEN}.dump $CONTAINER:/tmp/backup.dump
echo "✅ Copiado"

# 5. Crear BD destino
echo "🆕 Creando $DESTINO..."
docker exec $CONTAINER createdb -U $DB_ADMIN $DESTINO
echo "✅ Base creada"

# 6. Restaurar
echo "💾 Restaurando datos..."
docker exec $CONTAINER pg_restore -U $DB_ADMIN -d $DESTINO -c --no-owner /tmp/backup.dump
echo "✅ Datos restaurados"

# 7. Limpiar
echo "🧹 Limpiando..."
docker exec $CONTAINER rm /tmp/backup.dump
rm /tmp/${ORIGEN}.dump
echo "✅ Limpio"

# 8. Crear usuario si no existe
echo "👤 Configurando usuario $USUARIO..."
USER_EXISTS=$(docker exec $CONTAINER psql -U $DB_ADMIN -d postgres -t -c "SELECT 1 FROM pg_roles WHERE rolname='$USUARIO';" | xargs)
if [ "$USER_EXISTS" != "1" ]; then
    docker exec $CONTAINER psql -U $DB_ADMIN -d postgres -c "CREATE USER $USUARIO WITH PASSWORD '$PASSWORD';"
else
    docker exec $CONTAINER psql -U $DB_ADMIN -d postgres -c "ALTER USER $USUARIO WITH PASSWORD '$PASSWORD';"
fi
echo "✅ Usuario configurado"

# 9. Otorgar permisos
echo "🔐 Otorgando permisos..."
docker exec $CONTAINER psql -U $DB_ADMIN -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DESTINO TO $USUARIO;"
docker exec $CONTAINER psql -U $DB_ADMIN -d $DESTINO -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $USUARIO;"
docker exec $CONTAINER psql -U $DB_ADMIN -d $DESTINO -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $USUARIO;"
docker exec $CONTAINER psql -U $DB_ADMIN -d $DESTINO -c "ALTER SCHEMA public OWNER TO $USUARIO;"
docker exec $CONTAINER psql -U $DB_ADMIN -d postgres -c "ALTER DATABASE $DESTINO OWNER TO $USUARIO;"
echo "✅ Permisos otorgados"

# 10. Verificar
echo "📊 Verificando..."
TABLAS=$(docker exec $CONTAINER psql -U $DB_ADMIN -d $DESTINO -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';" | xargs)
echo "✅ $TABLAS tablas restauradas"

echo "=========================================="
echo "✅ ¡Clonación completada!"
echo "=========================================="
echo "📋 Datos de conexión:"
echo "   Base: $DESTINO"
echo "   Usuario: $USUARIO"
echo "   Password: $PASSWORD"
echo ""
echo "🔧 Para usar en Odoo, actualiza tu odoo.cfg:"
echo "   db_name = $DESTINO"
echo "   db_user = $USUARIO"
echo "   db_password = $PASSWORD"
echo "=========================================="