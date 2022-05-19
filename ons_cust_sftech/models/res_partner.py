# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    ons_measure_ids = fields.Many2many('ons.measure', string='Mesures')
    ons_bexio_id = fields.Integer()
