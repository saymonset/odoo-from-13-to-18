#!/bin/bash

echo "🛑 Deteniendo servicios Odoo..."

# Detener procesos de Odoo
echo "🔍 Buscando procesos Odoo..."
pkill -f "odoo-bin.*cliente1" || true
pkill -f "gevent.*cliente1" || true

# Esperar un momento para que los procesos terminen
sleep 2

# Forzar cierre si aún existen procesos
echo "⚡ Forzando cierre de procesos restantes..."
pkill -9 -f "odoo-bin.*cliente1" 2>/dev/null || true
pkill -9 -f "gevent.*cliente1" 2>/dev/null || true

# Liberar puertos
echo "🔓 Liberando puertos 48069 y 48070..."
sudo fuser -k 48069/tcp 2>/dev/null || true
sudo fuser -k 48070/tcp 2>/dev/null || true

# Verificación final
echo "🔎 Verificando estado final..."

# Verificar procesos
PROCESOS=$(pgrep -f "odoo-bin.*cliente1" | wc -l)
if [ $PROCESOS -eq 0 ]; then
    echo "✅ Todos los procesos Odoo han sido detenidos"
else
    echo "⚠️  Aún hay $PROCESOS proceso(s) activo(s):"
    pgrep -f "odoo-bin.*cliente1" | xargs ps -p 2>/dev/null || true
fi

# Verificar puertos
echo "🔍 Verificando estado de puertos..."
netstat -tlnp 2>/dev/null | grep -E '(48069|48070)' || echo "✅ Puertos 48069 y 48070 liberados"

# Mostrar logs recientes si existen
LOG_FILE="/home/odoo/odoo-from-13-to-18/arquitectura/odoo19/clientes/integraia_19/log/odoo.log"
if [ -f "$LOG_FILE" ]; then
    echo "📝 Últimas líneas del log (shutdown):"
    tail -n 3 "$LOG_FILE" | grep -i "shutdown\|stop\|exit" || echo "ℹ️  No se encontraron mensajes de cierre en el log"
fi

echo "🎯 Servicios Odoo detenidos correctamente"