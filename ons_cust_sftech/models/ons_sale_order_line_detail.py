# -*- coding: utf-8 -*-
# © 2022 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api
from odoo.tools.misc import get_lang


class OnsSaleOrderLineDetail(models.Model):
    _name = 'ons.sale.order.line.detail'
    _order = 'sale_order_line_id, sequence, id'

    sequence = fields.Integer(string='Sequence')
    display_type = fields.Selection([('line_section', "Section")], default=False)
    name = fields.Text(string='Description')
    body_part_id = fields.Many2one('ons.body.part', string='Catégorie')
    body_part_category_ids = fields.Many2many(
        'product.category', related='body_part_id.category_ids'
    )
    product_template_id = fields.Many2one('product.template', string='Produit')
    product_id = fields.Many2one('product.product', string='Article')
    product_qty = fields.Float(string='Quantité')
    product_uom_id = fields.Many2one(
        'uom.uom', string='Unité de mesure d\'article', related='product_id.uom_id'
    )
    sale_order_line_id = fields.Many2one('sale.order.line', string='Ligne de vente')
    
    partner_id = fields.Many2one(related="sale_order_line_id.order_id.partner_id")
    pricelist_id = fields.Many2one(related="sale_order_line_id.order_id.pricelist_id")
    company_id = fields.Many2one(related="sale_order_line_id.order_id.company_id")

    price_unit = fields.Float('Prix unitaire')
    price_subtotal = fields.Float('Sous-total', compute='_compute_price_subtotal')
    note = fields.Text(string='Commentaire')

    @api.onchange('product_id')
    def product_id_change(self):
        for detail in self:
            detail.product_template_id = detail.product_id.product_tmpl_id
            product = detail.product_id.with_context(
                lang=get_lang(
                    self.env, detail.sale_order_line_id.order_id.partner_id.lang
                ).code,
                partner=detail.sale_order_line_id.order_id.partner_id,
                quantity=detail.product_qty,
                date=detail.sale_order_line_id.order_id.date_order,
                pricelist=detail.sale_order_line_id.order_id.pricelist_id.id,
                uom=self.product_uom_id.id
            )
            detail.price_unit = self.env['account.tax']._fix_tax_included_price_company(
                detail.sale_order_line_id._get_display_price(product), product.taxes_id,
                detail.sale_order_line_id.tax_id, detail.sale_order_line_id.company_id
            )

    @api.onchange('product_template_id')
    def product_template_id_change(self):
        for detail in self:
            detail.product_id = detail.product_template_id.product_variant_id


    @api.depends('price_unit', 'product_qty')
    def _compute_price_subtotal(self):
        for detail in self:
            detail.price_subtotal = detail.price_unit * detail.product_qty
