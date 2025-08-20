import base64
from odoo import http


def user_company_service(self):
    user = http.request.env.user  # Obtiene el usuario actual
    company = user.company_id  # Obtiene la compañía asociada al usuario
    # Recopila información del usuario
    user_info = {
        "user_id": user.id,
        "user_name": user.name,
        "user_email": user.email,
    }

    # Recopila información de la compañía
    logo_url = ""
    if company.logo_web:
        # Asegúrate de que logo_web sea una cadena Base64
        logo_base64 = company.logo_web.decode("utf-8")
        # if isinstance(company.logo_web, bytes)
        # else company.logo_web
        # logo_url = f"data:image/png;base64,{logo_base64}"
        # # Convierte el logo a base64 y genera la URL
        # logo_base64 = company.logo_web.decode('utf-8')  # Convierte a base64 y decodifica a utf-8
        logo_url = f"data:image/png;base64,{logo_base64}"

        logo_base64 = base64.b64encode(company.logo_web).decode(
            "utf-8"
        )  # Convierte a base64 y decodifica a utf-8

    company_info = {
        "company_id": company.id,
        "company_name": company.name,
        "company_email": company.email,
        "company_phone": company.phone,
        "company_address": company.partner_id.contact_address,  # Dirección de la compañía
        "company_currency": company.currency_id.name,  # Moneda de la compañía
        "vat": company.vat,  # Número de identificación fiscal
        "logo": logo_url,  # URL del logo
    }

    return {
        "user": user_info,  # Devuelve la información del usuario
        "company": company_info,  # Devuelve la información de la compañía
    }
