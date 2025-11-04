#!/bin/bash

echo "🔄 Deteniendo servicios Odoo existentes..."
# Matar procesos más específicamente
pkill -f "odoo-bin.*gevent" || true
pkill -f "odoo-bin -c clientes/cliente1/conf/odoo.cfg" || true
sleep 5

echo "🔓 Liberando puertos..."
# Forzar liberación de puertos
sudo fuser -k 18069/tcp 2>/dev/null || true
sudo fuser -k 8072/tcp 2>/dev/null || true

# Esperar adicionalmente para asegurar liberación
sleep 3

# Verificar que los puertos estén libres
echo "📋 Verificando estado de puertos..."
if netstat -tln | grep -q ":18069 "; then
    echo "❌ Puerto 18069 todavía en uso, forzando liberación..."
    sudo fuser -k 18069/tcp 2>/dev/null || true
    sleep 2
fi

if netstat -tln | grep -q ":8072 "; then
    echo "❌ Puerto 8072 todavía en uso, forzando liberación..."
    sudo fuser -k 8072/tcp 2>/dev/null || true
    sleep 2
fi

echo "🚀 Iniciando servidor Odoo principal (puerto 18069)..."
cd /home/odoo/odoo-from-13-to-18/arquitectura/odoo18
./odoo/odoo-bin -c clientes/cliente1/conf/odoo.cfg &

echo "⏳ Esperando 15 segundos para que el servidor principal inicie..."
sleep 15

echo "🔌 Iniciando servidor Gevent/Longpolling (puerto 8072)..."
# Verificar que el puerto 8072 esté libre antes de iniciar
if netstat -tln | grep -q ":8072 "; then
    echo "⚠️  Puerto 8072 todavía ocupado, esperando..."
    sleep 3
    sudo fuser -k 8072/tcp 2>/dev/null || true
    sleep 2
    
    # Si después de liberar sigue ocupado, NO iniciar otro
    if netstat -tln | grep -q ":8072 "; then
        echo "✅ Puerto 8072 ya está en uso por un proceso Gevent existente. No se iniciará otro."
    else
        echo "🔄 Iniciando nuevo servidor Gevent..."
        ./odoo/odoo-bin gevent -c clientes/cliente1/conf/odoo.cfg &
    fi
else
    echo "🔄 Iniciando servidor Gevent..."
    ./odoo/odoo-bin gevent -c clientes/cliente1/conf/odoo.cfg &
fi

echo "✅ Servicios iniciados:"
echo "   - Principal: puerto 18069" 
echo "   - Longpolling: puerto 8072"

echo "📊 Verificando procesos..."
sleep 5
ps aux | grep odoo-bin | grep -v grep

echo "🌐 Verificando puertos..."
netstat -tlnp | grep -E '(18069|8072)' 2>/dev/null || echo "⚠️  Algunos puertos podrían no estar visibles aún"

echo "📝 Verificando logs de gevent..."
sleep 2
if [ -f "clientes/cliente1/log/odoo.log" ]; then
    echo "=== ÚLTIMAS LÍNEAS DEL LOG ==="
    tail -n 15 clientes/cliente1/log/odoo.log | grep -E "(8072|gevent|Evented|longpolling|Starting|Running)" || echo "ℹ️  No se encontraron entradas relevantes en el log"
else
    echo "⚠️  Archivo de log no encontrado: clientes/cliente1/log/odoo.log"
fi

echo "🎯 Verificación final - Procesos Odoo activos:"
ps aux | grep odoo-bin | grep -v grep | wc -l | xargs echo "Total de procesos:"

echo "✅ Si ves el puerto 8072 en uso y procesos activos, los servicios están funcionando."