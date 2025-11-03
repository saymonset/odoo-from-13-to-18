#!/bin/bash
# start_odoo_simple.sh - Script simplificado para Odoo 18

echo "🚀 Iniciando Odoo 18 con WebSocket integrado..."

cd /home/odoo/odoo-from-13-to-18/arquitectura/odoo18

# Detener servicios previos
echo "🛑 Deteniendo servicios previos..."
pkill -f "odoo-bin" || echo "No había procesos previos"
sleep 3

# Verificar y forzar cierre si es necesario
if pgrep -f "odoo-bin" > /dev/null; then
    echo "⚠️  Forzando cierre de procesos..."
    pkill -9 -f "odoo-bin"
    sleep 2
fi

# Iniciar Odoo (WebSocket integrado en el mismo proceso)
echo "🔧 Iniciando Odoo con WebSocket integrado (HTTP:18069, WebSocket:8072)..."
./odoo/odoo-bin -c clientes/cliente1/conf/odoo.cfg &

# Esperar inicio
echo "⏳ Esperando inicio del servidor..."
sleep 10

# Verificar
echo "📊 Verificando servicios..."
PID=$(pgrep -f "odoo-bin.*odoo.cfg")
if [ -n "$PID" ]; then
    echo "✅ Odoo ejecutándose (PID: $PID)"
else
    echo "❌ Odoo NO se pudo iniciar"
    exit 1
fi

# Verificar puertos
echo "🔌 Verificando puertos..."
netstat -tulpn | grep -E ':(18069|8072)' || echo "⚠️  Los puertos no están listos"

echo "🎯 Odoo iniciado correctamente con WebSocket integrado!"
echo "📝 Logs: tail -f clientes/cliente1/log/odoo.log"