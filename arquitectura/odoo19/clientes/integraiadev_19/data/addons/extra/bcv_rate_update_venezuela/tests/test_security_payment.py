from odoo.tests.common import TransactionCase
import logging

_logger = logging.getLogger(__name__)

class TestSecurityPayment(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Test Partner'})
        cls.product = cls.env['product.product'].create({
            'name': 'Test Product',
            'list_price': 100.0,
            'type': 'consu', # Consumable to avoid inventory validation issues during test
            'taxes_id': False,
            'supplier_taxes_id': False,
        })
        
    def test_01_malicious_payment_data_injection(self):
        """
        Verify that injecting malicious payment_data into a sale order
        (simulating an intercepted/altered frontend request)
        does NOT alter the actual amount_total of the order nor the invoice.
        """
        # Create a basic sale order
        order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 2.0,
                'price_unit': 100.0,
            })],
        })
        
        # Order total should be 200.0
        self.assertEqual(order.amount_total, 200.0, "El monto inicial de la orden debe ser 200.0")

        # Simular inyección maliciosa de datos de pago mediante sudo().write() 
        # (Esto imita lo que hace el controlador cuando recibe parámetros manipulados)
        malicious_payment_data = {
            'amount_vef': 5.0,  # El atacante intenta hacer creer que pagó 5.0
            'amount_usd': 1.0, 
            'exchange_rate': 5.0,
        }
        
        order.sudo().write({
            'payment_date': '2026-05-05',
            'payment_method': 'transfer',
            'amount_vef': malicious_payment_data['amount_vef'],
            'amount_usd': malicious_payment_data['amount_usd'],
            'exchange_rate': malicious_payment_data['exchange_rate'],
        })
        
        # 1. Asegurar que el total real de la orden SIGUE SIENDO 200.0 y no fue alterado por los valores inyectados
        self.assertEqual(
            order.amount_total, 
            200.0, 
            "⚠️ HUECO DE SEGURIDAD: ¡El amount_total de la orden fue alterado por datos de pago manipulados!"
        )
        
        # Confirmar la orden de venta
        order.action_confirm()
        
        # 2. Asegurar que el total de la orden se mantiene intacto tras la confirmación
        self.assertEqual(
            order.amount_total, 
            200.0, 
            "⚠️ HUECO DE SEGURIDAD: ¡El amount_total de la orden cambió tras ser confirmada!"
        )

        # Crear la factura desde la orden de venta
        invoice = order._create_invoices()
        
        # 3. Asegurar que el total de la factura es exactamente 200.0 (basado en los productos reales)
        self.assertEqual(
            invoice.amount_total, 
            200.0, 
            "⚠️ HUECO DE SEGURIDAD: ¡El amount_total de la factura fue alterado o arrastró la data manipulada!"
        )
        
        # 4. Asegurar que el precio unitario en las líneas de la factura se mantiene intacto
        self.assertEqual(
            invoice.invoice_line_ids[0].price_unit, 
            100.0, 
            "⚠️ HUECO DE SEGURIDAD: ¡El precio en las líneas de la factura fue modificado maliciosamente!"
        )

        _logger.info("✅ Todos los tests de seguridad pasaron: La integridad de la orden y la factura está protegida.")
