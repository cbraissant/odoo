# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, api
from odoo.exceptions import UserError
from PIL import Image
from io import BytesIO
import base64


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    ons_sale_order_line_id = fields.Many2one('sale.order.line', string='Ligne de vente')
    ons_sale_order_id = fields.Many2one(
        'sale.order',
        string='Vente',
        related='ons_sale_order_line_id.order_id',
        store=True
    )
    ons_client_id = fields.Many2one(
        'res.partner',
        string='Client',
        related='ons_sale_order_line_id.ons_client_id',
        store=True
    )
    ons_measure_ids = fields.Many2many(
        'ons.measure', related='ons_client_id.ons_measure_ids'
    )  # only used in ons_measure_id domain
    ons_measure_id = fields.Many2one('ons.measure', string='Mesures')
    ons_ref = fields.Char(string='Référence mesure', related='ons_measure_id.ref')
    ons_bexio_title = fields.Char(
        string='Référence', related='ons_sale_order_id.ons_bexio_title'
    )
    ons_mo_state = fields.Selection([
        ('patronage', 'Patronage'),
        ('cutting', 'Découpage'),
        ('collage', 'Collage'),
        ('aquassure', 'Aquassure'),
        ('test_sealing', 'Test d\'étanchéité'),
        ('accessories_mounting', 'Montage accessoires'),
        ('customer_information', 'Informations clients'),
    ],
                                    string='État de production',
                                    default='patronage',
                                    tracking=True)

    ons_note = fields.Text(string='Commentaire')
    ons_preview = fields.Binary(string='Preview')

    @api.onchange('ons_client_id')
    def _onchange_ons_client_id(self):
        for record in self:
            record.ons_measure_id = False

    # @api.onchange('move_raw_ids')
    # def _onchange_move_raw_ids(self):
    #     for record in self:
    #         im = Image.new("RGBA", (1200, 1200), (255, 255, 255, 0))
    #         for move_raw_id in record.move_raw_ids:
    #             move_raw_id.ons_label = move_raw_id.bom_line_id.ons_note
    #             b64_image = move_raw_id.product_id.ons_tag_ids.filtered(lambda x: x.name == move_raw_id.bom_line_id.ons_note).image_part
    #             if b64_image:
    #                 im2 = Image.open(BytesIO(base64.b64decode(b64_image)))
    #                 im2 = im2.convert("RGBA")
    #                 im.paste(im2, (0, 0), im2)
    #         buffer = BytesIO()
    #         im.save(buffer, format="PNG")
    #         record.ons_preview = base64.b64encode(buffer.getvalue())

    def _get_move_raw_values(
        self,
        product_id,
        product_uom_qty,
        product_uom,
        operation_id=False,
        bom_line=False
    ):
        data = super(MrpProduction, self)._get_move_raw_values(
            product_id, product_uom_qty, product_uom, operation_id, bom_line
        )
        data['ons_body_part_id'] = bom_line.ons_body_part_id.id
        data['ons_note'] = bom_line.ons_note
        return data

    def action_confirm(self):
        for record in self:
            for line in record.ons_measure_id.measure_line_ids:
                if line.to_check:
                    raise UserError('Au moins une mesure n\'a pas été vérifiée !')
        return super(MrpProduction, self).action_confirm()
