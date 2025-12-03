# -*- coding: utf-8 -*-
# from odoo import http


# class /home/simon/sharedFolder/odoo-skeleton/docker-instalacion-18/v18/addons/conversion(http.Controller):
#     @http.route('//home/simon/shared_folder/odoo-skeleton/docker-instalacion-18/v18/addons/conversion//home/simon/shared_folder/odoo-skeleton/docker-instalacion-18/v18/addons/conversion', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('//home/simon/shared_folder/odoo-skeleton/docker-instalacion-18/v18/addons/conversion//home/simon/shared_folder/odoo-skeleton/docker-instalacion-18/v18/addons/conversion/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('/home/simon/shared_folder/odoo-skeleton/docker-instalacion-18/v18/addons/conversion.listing', {
#             'root': '//home/simon/shared_folder/odoo-skeleton/docker-instalacion-18/v18/addons/conversion//home/simon/shared_folder/odoo-skeleton/docker-instalacion-18/v18/addons/conversion',
#             'objects': http.request.env['/home/simon/shared_folder/odoo-skeleton/docker-instalacion-18/v18/addons/conversion./home/simon/shared_folder/odoo-skeleton/docker-instalacion-18/v18/addons/conversion'].search([]),
#         })

#     @http.route('//home/simon/shared_folder/odoo-skeleton/docker-instalacion-18/v18/addons/conversion//home/simon/shared_folder/odoo-skeleton/docker-instalacion-18/v18/addons/conversion/objects/<model("/home/simon/shared_folder/odoo-skeleton/docker-instalacion-18/v18/addons/conversion./home/simon/shared_folder/odoo-skeleton/docker-instalacion-18/v18/addons/conversion"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('/home/simon/shared_folder/odoo-skeleton/docker-instalacion-18/v18/addons/conversion.object', {
#             'object': obj
#         })

