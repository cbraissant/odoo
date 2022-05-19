# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api


class OnsMeasureLine(models.Model):
    _name = 'ons.measure.line'
    _rec_name = 'type_id'

    measure_id = fields.Many2one('ons.measure')

    type_id = fields.Many2one('ons.measure.type', string='Désignation', required=True)
    measure_value = fields.Float(string='Mesure', required=True)
    measure_total = fields.Float(
        string='Total', compute='_compute_measure_total', store=True
    )
    to_check = fields.Boolean(string='À vérifier')

    type_number = fields.Integer(string='N°', related='type_id.number')
    type_name = fields.Char(string='Désignation', related='type_id.name')

    @api.depends('measure_id.suit_type', 'measure_value', 'type_id')
    def _compute_measure_total(self):
        for line in self:
            if line.measure_id.suit_type == 'neoprene_classic':
                line.measure_total = line.measure_value + line.type_id.ease_neoprene_classic
            elif line.measure_id.suit_type == 'neoprene_pro':
                line.measure_total = line.measure_value + line.type_id.ease_neoprene_pro
            elif line.measure_id.suit_type == 'tnt_classic':
                line.measure_total = line.measure_value + line.type_id.ease_tnt_classic
            elif line.measure_id.suit_type == 'tnt_pro':
                line.measure_total = line.measure_value + line.type_id.ease_tnt_pro
