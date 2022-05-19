# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    ons_bexio_id = fields.Integer()
    ons_tag_ids = fields.Many2many('ons.component.tag', string='Utilisable pour...')
    ons_is_suit = fields.Boolean(string='Combinaison')
