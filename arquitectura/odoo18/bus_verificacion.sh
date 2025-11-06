#!/bin/bash
# bus_verificacion.sh
# Verificación completa del BUS/WebSocket de Odoo

echo "🎯 VERIFICACIÓN FINAL DEL BUS"

# 1. Estado de los procesos Odoo
echo "1️⃣ Estado de Odoo:"
pgrep -af odoo || echo "⚠ Odoo no está corriendo como servicio o proceso"

# 2. Puertos activos (180xx)
echo "2️⃣ Puertos activos (180xx):"
netstat -tulpn | grep 180 || echo "⚠ No se detectan puertos Odoo activos"

# 3. Procesos Odoo
echo "3️⃣ Procesos Odoo:"
ps aux | grep odoo | grep -v grep

# 4. Configuración Nginx
echo "4️⃣ Test de configuración Nginx:"
sudo nginx -t

# 5. Test de endpoints BUS/Longpolling
echo "5️⃣ Test de endpoints Longpolling:"
echo -n "   - /longpolling/: "
curl -s -o /dev/null -w "%{http_code}\n" "https://jumpjibe.com/longpolling/" || echo "FAIL"

# 6. Logs recientes de BUS/WebSocket/Longpolling
echo "6️⃣ Últimos logs de BUS:"
tail -20 ~/odoo-from-13-to-18/arquitectura/odoo18/clientes/cliente1/log/odoo.log | grep -i "bus\|websocket\|longpolling"

echo "✅ Verificación completada"
