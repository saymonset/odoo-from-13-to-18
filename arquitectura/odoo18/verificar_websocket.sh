#!/bin/bash
# diagnose_version.sh

echo "🔍 DIAGNÓSTICO DE VERSIÓN WEBSOCKET"
echo "==================================="

echo "1. ✅ Verificando versión de Odoo..."
grep -i "version" /home/odoo/odoo-from-13-to-18/arquitectura/odoo18/odoo/__init__.py

echo ""
echo "2. ✅ Verificando logs de WebSocket..."
tail -20 /home/odoo/odoo-from-13-to-18/arquitectura/odoo18/clientes/cliente1/log/odoo.log | grep -E "version|websocket|OUTDATED" | tail -10

echo ""
echo "3. ✅ Probando diferentes versiones localmente..."
versions=("18.0" "18.0-7" "18.0.0" "18")
for version in "${versions[@]}"; do
    echo "🔗 Probando versión: $version"
    curl -s -o /dev/null -w "Código: %{http_code}\n" \
         -H "Upgrade: websocket" \
         -H "Connection: Upgrade" \
         "http://127.0.0.1:8072/websocket?version=$version" &
    sleep 1
done

echo ""
echo "🎯 DIAGNÓSTICO COMPLETADO"