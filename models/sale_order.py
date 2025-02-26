from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_rental_order = fields.Boolean()
    rental_start_date = fields.Datetime()
    rental_return_date = fields.Datetime()
    duration_days = fields.Integer(compute="_compute_duration_days")
    rental_status = fields.Selection(
        [
            ('draft', 'Draft'),
            ('reserved', 'Reserved'),
            ('returned', 'Returned'),
            ('cancelled', 'Cancelled'),
        ],
        default='draft',
        string='Rental Status'
    )

    @api.depends("rental_start_date", "rental_return_date")
    def _compute_duration_days(self):
        for rec in self:
            if rec.rental_start_date and rec.rental_return_date:
                start_date = rec.rental_start_date.replace(hour=0, minute=0, second=0)
                return_date = rec.rental_return_date.replace(hour=0, minute=0, second=0)
                rec.duration_days = (return_date - start_date).days
            else:
                rec.duration_days = 0

    def action_confirm(self):
        result = super(SaleOrder, self).action_confirm()
        today = fields.Datetime.now()
        for record in self:
            if record.rental_start_date and record.rental_return_date:
                if record.rental_start_date <= today <= record.rental_return_date:
                    record.rental_status = "reserved"
            else:
                raise ValidationError(_("Start Date and Return Date can not be empty"))
        return result

    def action_rental_sales_confirm(self):
        today = fields.Datetime.now()
        for rec in self:
            if rec.rental_start_date and rec.rental_return_date:
                if rec.rental_start_date <= today <= rec.rental_return_date:
                    rec.rental_status = "reserved"

    def action_rental_sales_reserve(self):
        for rec in self:
            rec.rental_status = 'reserved'

    def action_rental_sales_returned(self):
        for rec in self:
            rec.rental_status = 'returned'

    