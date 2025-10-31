import time

print("=== DIAGNÓSTICO COMPLETO MÓDULO BUS ===")

# 1. Verificar módulo bus
print("\n1. VERIFICANDO MÓDULO BUS...")
bus_module = env['ir.module.module'].search([('name','=','bus')], limit=1)
if not bus_module:
    print("❌ ERROR: Módulo bus no encontrado")
else:
    print(f"✅ Módulo bus encontrado - Estado: {bus_module.state}")

# 2. Reinstalar módulo bus
print("\n2. REINSTALANDO MÓDULO BUS...")
if bus_module.state == 'installed':
    print("Desinstalando...")
    bus_module.button_immediate_uninstall()
    env.cr.commit()
    time.sleep(2)

print("Instalando...")
bus_module.button_immediate_install()
env.cr.commit()
time.sleep(3)

# 3. Verificar estado final
print("\n3. VERIFICANDO ESTADO FINAL...")
bus_module = env['ir.module.module'].search([('name','=','bus')], limit=1)
print(f"Estado final del módulo bus: {bus_module.state}")

# 4. Verificar controladores
print("\n4. VERIFICANDO CONTROLADORES...")
BusController = env['ir.http']._get_controller_class('/longpolling/poll')
if BusController:
    print(f"✅ Controlador /longpolling/poll encontrado: {BusController}")
else:
    print("❌ Controlador /longpolling/poll NO encontrado")

# 5. Verificar configuración
print("\n5. VERIFICANDO CONFIGURACIÓN...")
from odoo.tools import config
print(f"longpolling_port: {config.get('longpolling_port')}")
print(f"gevent_port: {config.get('gevent_port')}")
print(f"server_wide_modules: {config.get('server_wide_modules')}")

print("\n=== DIAGNÓSTICO COMPLETADO ===")