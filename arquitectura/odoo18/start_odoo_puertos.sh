#!/bin/bash

echo "🔄 Deteniendo servicios Odoo existentes..."
sudo pkill -f "odoo-bin" || true
sleep 5

echo "🔓 Liberando puertos 18069 y 18070..."
sudo fuser -k 18069/tcp 2>/dev/null || true
sudo fuser -k 18070/tcp 2>/dev/null || true
sleep 3

echo "🧹 Limpiando archivo de configuración..."
cd /home/odoo/odoo-from-13-to-18/arquitectura/odoo18 || {
    echo "❌ No se pudo acceder al directorio de Odoo"
    exit 1
}

# Asegurar configuración correcta en el archivo odoo.cfg
CONFIG_FILE="clientes/cliente1/conf/odoo.cfg"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Archivo de configuración no encontrado: $CONFIG_FILE"
    exit 1
fi

# Actualizar gevent_port a 18070
sed -i 's/^gevent_port\s*=.*$/gevent_port = 18070/' "$CONFIG_FILE"

# Desactivar longpolling_port (debe estar en False o comentado)
# if grep -q '^longpolling_port' "$CONFIG_FILE"; then
#     sed -i 's/^longpolling_port\s*=.*$/longpolling_port = False/' "$CONFIG_FILE"
# else
#     echo "longpolling_port = False" >> "$CONFIG_FILE"
# fi

echo "🔍 Verificando configuración relevante:"
grep -E "^(gevent_port|longpolling_port|workers)" "$CONFIG_FILE"

echo "🚀 Iniciando servidor Odoo principal (gevent se inicia automáticamente)..."
nohup ./odoo/odoo-bin -c "$CONFIG_FILE" > clientes/cliente1/log/odoo.log 2>&1 &

echo "⏳ Esperando 25 segundos para que el servicio se inicie..."
sleep 25

echo "✅ Verificación de servicios:"
echo "📊 Procesos Odoo activos:"
ps aux | grep odoo-bin | grep -v grep

echo "🌐 Puertos en uso (18069 y 18070):"
if command -v netstat >/dev/null 2>&1; then
    netstat -tln 2>/dev/null | grep -E '(18069|18070)' || echo "No se encontraron puertos con netstat"
else
    echo "netstat no disponible, intentando con ss..."
    sudo ss -tlnp | grep -E '(18069|18070)' || echo "No se encontraron puertos con ss"
fi

echo "📝 Verificando logs recientes (últimas 20 líneas):"
if [ -f "clientes/cliente1/log/odoo.log" ]; then
    echo "=== BUSCANDO GEVENT EN LOGS ==="
    tail -n 20 clientes/cliente1/log/odoo.log | grep -i -E "gevent|longpolling|18070" || echo "No se encontraron referencias específicas en logs"
else
    echo "❌ Archivo de log no encontrado"
fi

echo "🎯 RESUMEN FINAL:"
echo "   - Servidor principal: puerto 18069"
echo "   - Longpolling/Gevent: puerto 18070 (iniciado automáticamente por workers)"
echo "   - Workers configurados: 2"
