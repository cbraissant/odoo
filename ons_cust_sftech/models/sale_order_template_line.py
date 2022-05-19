# -*- coding: utf-8 -*-
# © 2022 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api


class SaleOrderTemplateLine(models.Model):
    _inherit = 'sale.order.template.line'

    ons_detail_ids = fields.One2many(
        'ons.sale.order.template.line.detail',
        'sale_order_template_line_id',
        string='Détails',
        copy=True
    )
