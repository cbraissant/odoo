# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    ons_client_id = fields.Many2one('res.partner', string='Client')
    ons_measure_id = fields.Many2one('ons.measure', string='Mesures')
    ons_measure_ids = fields.Many2many(
        'ons.measure', related='ons_client_id.ons_measure_ids'
    )  # only used in ons_measure_id domain
    ons_detail_ids = fields.One2many(
        'ons.sale.order.line.detail', 'sale_order_line_id', string='Détails', copy=True
    )
    ons_note = fields.Text(string='Commentaire')
    ons_sol_accessories_id = fields.Many2one('sale.order.line')

    @api.model
    def create(self, vals):
        res = super(SaleOrderLine, self).create(vals)
        if self.ons_detail_ids:
            vals['ons_sol_accessories_id'] = self.create_or_update_accessories_id()
        return res

    def write(self, vals):
        res = super(SaleOrderLine, self).write(vals)
        if self.ons_detail_ids:
            vals['ons_sol_accessories_id'] = self.create_or_update_accessories_id()
        return res

    def create_or_update_accessories_id(self):
        product = self.env.ref('ons_cust_sftech.product_accessories')
        sol = {
            'product_id': product.id,
            'order_id': self.order_id.id,
            'price_unit': sum(self.ons_detail_ids.mapped('price_subtotal')),
            'product_uom_qty': self.product_uom_qty,
            'product_uom': product.uom_id.id,
        }
        if self.ons_sol_accessories_id:
            self.ons_sol_accessories_id.write(sol)
        else:
            self.ons_sol_accessories_id = self.env['sale.order.line'].create(sol)
        return self.ons_sol_accessories_id.id
