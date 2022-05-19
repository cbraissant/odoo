# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    ons_body_part_id = fields.Many2one('ons.body.part', string='Article')
    ons_note = fields.Char(string='Commentaire')
