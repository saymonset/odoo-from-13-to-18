from odoo import http


class T-shirt-inventario(http.Controller):
    
    @http.route('/api/tshirts', auth='public', methods=['GET'], type='http')
    def get_top10_tshirts(self, **kwargs):
        """
        Endpoint que devuelve los 10 registros principales de camisetas
        """
        try:
            # Buscar las 10 camisetas principales (puedes ajustar el dominio)
            tshirts = request.env['product.product'].search([
                ('categ_id.name', 'ilike', 'camiseta')  # Filtrar por categoría camiseta
            ], limit=10)
            
            # Preparar los datos para JSON
            tshirts_data = []
            for tshirt in tshirts:
                tshirts_data.append({
                    'id': tshirt.id,
                    'name': tshirt.name,
                    'default_code': tshirt.default_code or '',
                    'barcode': tshirt.barcode or '',
                    'list_price': tshirt.list_price,
                    'qty_available': tshirt.qty_available,
                    'category': tshirt.categ_id.name if tshirt.categ_id else '',
                    'image_url': f'/web/image/product.product/{tshirt.id}/image_128' if tshirt.image_128 else ''
                })
            
            # Devolver como JSON
            return http.Response(
                json.dumps({
                    'success': True,
                    'count': len(tshirts_data),
                    'tshirts': tshirts_data
                }),
                content_type='application/json'
            )
            
        except Exception as e:
            return http.Response(
                json.dumps({
                    'success': False,
                    'error': str(e)
                }),
                content_type='application/json',
                status=500
            )

    