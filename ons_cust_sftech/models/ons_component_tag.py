# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields


class ComponentTag(models.Model):
    _name = 'ons.component.tag'

    name = fields.Char(string='Infos')
    image_part = fields.Binary(string='Image')
