# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api

suit_types = [('neoprene_classic', 'Néoprène Classic'), ('neoprene_pro', 'Néoprène Pro'),
              ('tnt_classic', 'TNT Classic'), ('tnt_pro', 'TNT Pro')]


class OnsMeasure(models.Model):
    _name = 'ons.measure'

    name = fields.Char(string='Désignation', store=True, compute='_compute_name')
    date = fields.Date(string='Date de la prise de mesure', required=True)
    ref = fields.Char(string='Référence')
    partner_taking_measure_id = fields.Many2one(
        'res.partner', string='Personne ayant pris la mesure'
    )
    note = fields.Text(string='Commentaire')

    suit_type = fields.Selection(suit_types, string='Type de combinaison', required=True)

    gender = fields.Selection([('m', 'Homme'), ('f', 'Femme')],
                              string='Genre',
                              required=True)
    size = fields.Float(string='Taille [cm]', required=True)
    weight = fields.Float(string='Poids [kg]', required=True)
    shoe_size = fields.Selection([('28', '28'), ('28.5', '28.5'), ('29', '29'),
                                  ('29.5', '29.5'), ('30', '30'), ('30.5', '30.5'),
                                  ('31', '31'), ('31.5', '31.5'), ('32', '32'),
                                  ('32.5', '32.5'), ('33', '33'), ('33.5', '33.5'),
                                  ('34', '34'), ('34.5', '34.5'), ('35', '35'),
                                  ('35.5', '35.5'), ('36', '36'), ('36.5', '36.5'),
                                  ('37', '37'), ('37.5', '37.5'), ('38', '38'),
                                  ('38.5', '38.5'), ('39', '39'), ('39.5', '39.5'),
                                  ('40', '40'), ('40.5', '40.5'), ('41', '41'),
                                  ('41.5', '41.5'), ('42', '42'), ('42.5', '42.5'),
                                  ('43', '43'), ('43.5', '43.5'), ('44', '44'),
                                  ('44.5', '44.5'), ('45', '45'), ('45.5', '45.5'),
                                  ('46', '46'), ('46.5', '46.5'), ('47', '47'),
                                  ('47.5', '47.5'), ('48', '48'), ('48.5', '48.5'),
                                  ('49', '49'), ('49.5', '49.5'), ('50', '50'),
                                  ('50.5', '50.5'), ('51', '51'), ('51.5', '51.5'),
                                  ('52', '52'), ('52.5', '52.5'), ('53', '53'),
                                  ('53.5', '53.5'), ('54', '54')],
                                 string='Pointure',
                                 required=True)

    measure_line_ids = fields.One2many(
        'ons.measure.line', 'measure_id', string='Mesures'
    )
    show_button = fields.Boolean(default=True)

    calcul_shoulder = fields.Char(
        string='Valeur épaule (#8)', compute='check_measures', store=True
    )
    checked_shoulder = fields.Boolean(
        string='Épaule', compute='check_measures', store=True
    )
    calcul_torso = fields.Char(
        string='Valeur haut torse (#20)', compute='check_measures', store=True
    )
    checked_torso = fields.Boolean(
        string='Haut torse', compute='check_measures', store=True
    )

    @api.depends('ref', 'suit_type', 'date')
    def _compute_name(self):
        for measure in self:
            suit_type = next(
                suit_type[1]
                for suit_type in suit_types if suit_type[0] == measure.suit_type
            )
            measure.name = '{} / {} / {}'.format(measure.ref, suit_type, measure.date)

    def default_measure_line_ids(self):
        for measure in self:
            measure_types_ids = self.env['ons.measure.type'].search([])
            measure_line_ids = []
            for type in measure_types_ids:
                measure_line_ids.append(
                    self.env['ons.measure.line'].create({
                        'type_id': type.id,
                        'measure_value': 0,
                    }).id
                )
            measure.measure_line_ids = measure_line_ids
            measure.show_button = False
            return measure_line_ids

    @api.depends('measure_line_ids')
    def check_measures(self):
        for measure in self:
            lines_by_number = dict()
            for line in measure.measure_line_ids:
                lines_by_number[line.type_number] = line
            if len(lines_by_number) >= 20:
                value_shoulder = 2 * (
                    lines_by_number[6].measure_value - lines_by_number[7].measure_value
                )
                measure.calcul_shoulder = 'Épaule: 2 * ({} - {}) = {}'.format(
                    lines_by_number[6].measure_value, lines_by_number[7].measure_value,
                    value_shoulder
                )
                measure.checked_shoulder = value_shoulder == lines_by_number[
                    5].measure_value

                value_torso = lines_by_number[19].measure_value - lines_by_number[
                    17].measure_value
                measure.calcul_torso = 'Haut torse: {} - {} = {}'.format(
                    lines_by_number[19].measure_value, lines_by_number[17].measure_value,
                    value_torso
                )
                measure.checked_torso = value_torso == lines_by_number[20].measure_value
