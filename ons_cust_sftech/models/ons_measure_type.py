# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields


class OnsMeasureType(models.Model):
    _name = 'ons.measure.type'

    name = fields.Char(string='Désignation', required=True)
    number = fields.Integer(string='N°', required=True)

    ease_neoprene_classic = fields.Float(
        string='Valeur pour Néoprène Classic', required=True
    )
    ease_neoprene_pro = fields.Float(string='Valeur pour Néoprène Pro', required=True)
    ease_tnt_classic = fields.Float(string='Valeur pour TNT Classic', required=True)
    ease_tnt_pro = fields.Float(string='Valeur pour TNT Pro', required=True)
