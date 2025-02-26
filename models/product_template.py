from odoo import models, fields, api, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    count_rent = fields.Integer(string = 'Count Rent', compute = '_compute_count_rent')
    is_rent  = fields.Boolean(string='Can be rented')

    @api.depends('is_rent')
    def _compute_count_rent(self):
        for record in self:
            record.count_rent = self.env['sale.order.line'].search_count([
                ('product_template_id', '=', record.id),
                ('order_id.rental_status', '=', 'reserved')
            ])

    # def action_rental_products(self):
    #     return {
    #         "name": _("Rental Product"),
    #         "type": "ir.actions.act_window",
    #         "view_mode": "tree,form",
    #         "res_model": "product.template",
    #         "target": "current",
    #         "domain": [("is_rent", "=", True)],
    #         "context": {"default_is_rent": self.id}
    #     }

    # def action_open_sale_order(self):
    #     # Ambil ID produk.product dari product.template
    #     product_ids = self.env['product.product'].search([('product_tmpl_id', '=', self.id)]).ids
    #     # Cari sale.order yang memiliki order_line dengan produk terkait
    #     sale_orders = self.env['sale.order'].search([('order_line.product_id', 'in', product_ids)])
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Sale Order',
    #         'view_mode': 'tree,form',
    #         'res_model': 'sale.order',
    #         'domain': [('id', 'in', sale_orders.ids)],  # Filter hanya sale order yang terkait
    #         'context': {'default_order_line.product_id': product_ids[0] if product_ids else False},  
    #     }

    def action_open_sale_order(self):
        """Show Sale Orders where this product is rented and in Reserved status"""
        sale_orders = self.env['sale.order.line'].search([
            ('product_id.product_tmpl_id', '=', self.id),
            ('order_id.rental_status', '=', 'reserved')
        ]).mapped('order_id')

        return {
            'name': 'Reserved Sale Orders',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': [('id', 'in', sale_orders.ids)],
            'views': [(self.env.ref('rental_sales.view_sale_order_reserved_tree').id, 'tree'),
                  (False, 'form')],
            'context': {'default_rental_status': 'reserved'},
        }