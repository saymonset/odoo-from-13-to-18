#!/bin/bash

# Activar entorno virtual
echo "Activando entorno virtual..."
source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Error al activar el entorno virtual"
    exit 1
fi

# Puerto, base de datos y rutas
PORT=38069
DB="dbintegraiadev_19"
ODOO_BIN="./odoo/odoo-bin"
ODOO_CONF="clientes/integraiadev_19/conf/odoo.cfg"

# --- SOLUCIÓN: regenerar assets antes de arrancar ---
# echo "Regenerando assets (web) para solucionar filestore corrupto..."
# $ODOO_BIN -d $DB -c $ODOO_CONF --update=web --stop-after-init
# if [ $? -ne 0 ]; then
#     echo "Error al regenerar assets. Revisa la base de datos o filestore."
#     exit 1
# fi
# ----------------------------------------------------

echo "Verificando si hay procesos usando el puerto $PORT..."
PIDS=$(sudo lsof -t -i :$PORT)
if [ ! -z "$PIDS" ]; then
    echo "Matando procesos en el puerto $PORT: $PIDS"
    sudo kill -9 $PIDS
else
    echo "No hay procesos usando el puerto $PORT"
fi

echo "Iniciando Odoo..."
$ODOO_BIN -d $DB -c $ODOO_CONF --dev=all