# -*- coding: utf-8 -*-
# © 2022 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields


class OnsBodyPart(models.Model):
    _name = 'ons.body.part'

    name = fields.Char(string='Nom', translate=True, required=True)
    category_ids = fields.Many2many('product.category', string='Catégories')
