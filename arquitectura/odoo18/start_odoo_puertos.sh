#!/bin/bash

echo "🔄 Deteniendo servicios Odoo existentes..."
pkill -f odoo-bin
pkill -f gevent
sleep 3

echo "🔓 Liberando puertos..."
sudo fuser -k 18069/tcp 2>/dev/null || true
sudo fuser -k 8072/tcp 2>/dev/null || true

echo "🚀 Iniciando servidor Odoo principal (puerto 18069)..."
cd /home/odoo/odoo-from-13-to-18/arquitectura/odoo18
./odoo/odoo-bin -c clientes/cliente1/conf/odoo.cfg &

echo "⏳ Esperando 10 segundos para que el servidor principal inicie..."
sleep 10

echo "🔌 Iniciando servidor Gevent/Longpolling (puerto 8072)..."
./odoo/odoo-bin gevent -c clientes/cliente1/conf/odoo.cfg &

echo "✅ Servicios iniciados:"
echo "   - Principal: puerto 18069" 
echo "   - Longpolling: puerto 8072"

echo "📊 Verificando procesos..."
sleep 5
ps aux | grep odoo-bin | grep -v grep

echo "🌐 Verificando puertos..."
netstat -tlnp | grep -E '(18069|8072)'

echo "📝 Verificando logs de gevent..."
tail -n 5 clientes/cliente1/log/odoo.log | grep -E "(8072|gevent|Evented)"

echo "🎯 Si ves 'Evented Service (longpolling) running on 0.0.0.0:8072' en los logs, ¡éxito!"