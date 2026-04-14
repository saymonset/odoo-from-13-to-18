#!/bin/bash
# eliminar_modulo.sh

CONTAINER="odoo-db19-test"
DB_USER="odoo"
DB_NAME="dbintegraia_19"
MODULE="l10n_ve_currency_rate_live"

echo "Eliminando módulo: $MODULE"

docker exec "$CONTAINER" bash -c "
psql -U $DB_USER -d $DB_NAME << EOF
-- Verificar antes de eliminar
SELECT id, name, state FROM ir_module_module WHERE name = '$MODULE';

-- Eliminar el módulo
DELETE FROM ir_module_module WHERE name = '$MODULE';

-- Buscar tablas residuales
SELECT table_name FROM information_schema.tables 
WHERE table_name LIKE '%${MODULE}%';

-- Verificar que se eliminó
SELECT id, name, state FROM ir_module_module WHERE name = '$MODULE';
EOF
"

echo "Módulo eliminado correctamente"