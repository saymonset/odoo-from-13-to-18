#!/bin/bash


## Si es la primera vez que se ejecuta, iniciar bdcon esto
# ir a consola
# source .venv/bin/activate
# ./odoo/odoo-bin -d dbcliente1_19 -i base -c clientes/cliente1/conf/odoo.cfg


# Luego salir con ctrl+D y ejecutar este script
# Script para levantar Odoo cliente1 con entorno virtual

# Activar entorno virtual
echo "Activando entorno virtual..."
source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Error al activar el entorno virtual"
    exit 1
fi

# Puerto por defecto de Odoo
PORT=8069

# Base de datos
DB="dbcliente1_19"

# Ruta a odoo-bin
ODOO_BIN="./odoo/odoo-bin"

# Config
ODOO_CONF="clientes/cliente1/conf/odoo.cfg"

echo "Verificando si hay procesos usando el puerto $PORT..."

# Buscar procesos en el puerto y matarlos
PIDS=$(sudo lsof -t -i :$PORT)
if [ ! -z "$PIDS" ]; then
    echo "Matando procesos en el puerto $PORT: $PIDS"
    sudo kill -9 $PIDS
else
    echo "No hay procesos usando el puerto $PORT"
fi

# Levantar Odoo
echo "Iniciando Odoo..."
$ODOO_BIN -d $DB -c $ODOO_CONF --dev=all
