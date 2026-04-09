#!/bin/bash

echo "=========================================="
echo "🔄 Clonando dbodoo19 a dbhoteljumpjibe_19"
echo "=========================================="

# 1. Eliminar base de datos existente
echo "🗑️ Eliminando dbhoteljumpjibe_19 existente..."
docker exec odoo-db19-n8n dropdb -U odoo dbhoteljumpjibe_19 2>/dev/null || echo "No existía"

# 2. Crear backup de dbodoo19
echo "📦 Creando backup de dbodoo19..."
docker exec odoo-db19-n8n pg_dump -U odoo -F c dbodoo19 > /tmp/dbodoo19_backup.dump

# 3. Copiar backup al contenedor
echo "📁 Copiando backup al contenedor..."
docker cp /tmp/dbodoo19_backup.dump odoo-db19-n8n:/tmp/

# 4. Crear nueva base de datos
echo "🆕 Creando dbhoteljumpjibe_19..."
docker exec odoo-db19-n8n createdb -U odoo dbhoteljumpjibe_19

# 5. Restaurar backup en nueva base
echo "💾 Restaurando datos en dbhoteljumpjibe_19..."
docker exec odoo-db19-n8n pg_restore -U odoo -d dbhoteljumpjibe_19 -c --no-owner /tmp/dbodoo19_backup.dump

# 6. Limpiar archivos temporales
echo "🧹 Limpiando archivos temporales..."
docker exec odoo-db19-n8n rm /tmp/dbodoo19_backup.dump
rm /tmp/dbodoo19_backup.dump

# 7. Verificar que el usuario hoteljumpjibe_19 existe
echo "👤 Verificando usuario hoteljumpjibe_19..."
USER_EXISTS=$(docker exec odoo-db19-n8n psql -U odoo -d postgres -t -c "SELECT 1 FROM pg_roles WHERE rolname='hoteljumpjibe_19';" | xargs)

if [ "$USER_EXISTS" != "1" ]; then
    echo "📝 Creando usuario hoteljumpjibe_19..."
    docker exec odoo-db19-n8n psql -U odoo -d postgres -c "CREATE USER hoteljumpjibe_19 WITH PASSWORD 'hoteljumpjibe_2024';"
else
    echo "✅ Usuario hoteljumpjibe_19 ya existe"
fi

# 8. Otorgar todos los privilegios al usuario
echo "🔐 Otorgando privilegios a hoteljumpjibe_19 sobre dbhoteljumpjibe_19..."
docker exec odoo-db19-n8n psql -U odoo -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE dbhoteljumpjibe_19 TO hoteljumpjibe_19;"

# 9. Otorgar privilegios sobre todas las tablas (importante para Odoo)
echo "📋 Otorgando privilegios sobre todas las tablas..."
docker exec odoo-db19-n8n psql -U odoo -d dbhoteljumpjibe_19 -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO hoteljumpjibe_19;"
docker exec odoo-db19-n8n psql -U odoo -d dbhoteljumpjibe_19 -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO hoteljumpjibe_19;"
docker exec odoo-db19-n8n psql -U odoo -d dbhoteljumpjibe_19 -c "ALTER SCHEMA public OWNER TO hoteljumpjibe_19;"

# 10. Cambiar owner de la base de datos
echo "👑 Cambiando owner de la base de datos..."
docker exec odoo-db19-n8n psql -U odoo -d postgres -c "ALTER DATABASE dbhoteljumpjibe_19 OWNER TO hoteljumpjibe_19;"

echo "=========================================="
echo "✅ Base de datos clonada exitosamente"
echo "=========================================="

# 11. Verificar
echo "📊 Verificando..."
docker exec odoo-db19-n8n psql -U odoo -d dbhoteljumpjibe_19 -c "SELECT COUNT(*) FROM res_users;"

echo ""
echo "🔐 Permisos otorgados a hoteljumpjibe_19:"
echo "   - Todos los privilegios sobre la base de datos"
echo "   - Todos los privilegios sobre todas las tablas"
echo "   - Owner del esquema public"
echo "   - Owner de la base de datos"
echo ""
echo "🌐 Para usar esta base con Odoo, cambia en odoo.conf:"
echo "  db_name = dbhoteljumpjibe_19"
echo "  db_user = hoteljumpjibe_19"
echo "  db_password = hoteljumpjibe_2024"
echo ""
echo "Para cambiar la configuración de Odoo:"
echo "  docker exec odoo-19-web sed -i 's/db_name = dbodoo19/db_name = dbhoteljumpjibe_19/g' /etc/odoo/odoo.conf"
echo "  docker exec odoo-19-web sed -i 's/db_user = odoo/db_user = hoteljumpjibe_19/g' /etc/odoo/odoo.conf"
echo "  docker restart odoo-19-web"
echo "=========================================="