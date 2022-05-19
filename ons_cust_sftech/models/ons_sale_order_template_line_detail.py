# -*- coding: utf-8 -*-
# © 2022 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields


class OnsSaleOrderTemplateLineDetail(models.Model):
    _name = 'ons.sale.order.template.line.detail'
    _order = 'sale_order_template_line_id, sequence, id'

    sequence = fields.Integer(string='Sequence')
    display_type = fields.Selection([('line_section', "Section")], default=False)
    name = fields.Text(string='Description', translate=True)
    body_part_id = fields.Many2one('ons.body.part', string='Catégorie')
    body_part_category_ids = fields.Many2many(
        'product.category', related='body_part_id.category_ids'
    )
    product_id = fields.Many2one('product.product', string='Produit')
    product_qty = fields.Float(string='Quantité')
    product_uom_id = fields.Many2one(
        'uom.uom', string='Unité de mesure d\'article', related='product_id.uom_id'
    )
    sale_order_template_line_id = fields.Many2one(
        'sale.order.template.line', string='Ligne de vente'
    )
