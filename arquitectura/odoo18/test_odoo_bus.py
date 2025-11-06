#!/usr/bin/env python3
# test_odoo_bus_longpoll.py
import requests

url = "https://jumpjibe.com/longpolling/poll"
cookies = {"session_id": "TU_SESSION_DE_USUARIO_ODDO"}  # Debes autenticarte primero

try:
    r = requests.post(url, cookies=cookies, json={"channels": [["dbcliente1_18", "res.partner", "create"]]})
    print("✅ Conectado al longpolling, respuesta:", r.text)
except Exception as e:
    print("❌ Error:", e)
