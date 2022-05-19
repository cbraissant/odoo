# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api
from odoo.tests.common import Form
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    ons_bexio_name = fields.Char(string='Référence Bexio')
    ons_bexio_title = fields.Char(string='Référence')
    ons_bexio_date = fields.Date(string='Date Bexio')
    ons_bexio_id = fields.Integer(string='ID Bexio')

    ons_mrp_production_ids = fields.One2many('mrp.production', 'ons_sale_order_id')
    ons_mrp_production_count = fields.Integer(
        compute='_compute_ons_mrp_production_count', store=True
    )

    ons_picking_state = fields.Selection([
        ('draft', 'Brouillon'),
        ('waiting', 'En attente d\'une autre opération'),
        ('confirmed', 'En attente'),
        ('assigned', 'Prêt'),
        ('done', 'Fait'),
        ('cancel', 'Annulé'),
        ('mix', 'Plusieurs états'),
        ('no_picking', 'Pas de bulletin de livraison'),
    ],
                                         string='Statut de la livraison',
                                         compute='_compute_ons_picking_state')

    def onchange_sale_order_template_id(self):
        res = super(SaleOrder, self).onchange_sale_order_template_id()
        for line in self.order_line:
            line.ons_client_id = self.partner_id
        return res

    def _compute_line_data_for_template_change(self, line):
        data = super(SaleOrder, self)._compute_line_data_for_template_change(line)
        data['ons_detail_ids'] = [(
            0, 0, {
                'sequence': detail.sequence,
                'display_type': detail.display_type,
                'name': detail.name,
                'body_part_id': detail.body_part_id.id,
                'product_id': detail.product_id.id,
                'product_qty': detail.product_qty,
                'product_uom_id': detail.product_uom_id.id,
            }
        ) for detail in line.ons_detail_ids]
        return data

    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        self.create_or_update_product_and_bom()
        return res

    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        self.create_or_update_product_and_bom()
        return res

    def create_or_update_product_and_bom(self):
        for so in self:
            if so.state == 'draft':
                for line in so.order_line:
                    if line.ons_detail_ids:
                        product_data = {
                            'name': line.product_template_id.name,
                            'active': False,
                        }
                        if line.product_template_id.bom_ids and not line.product_template_id.ons_is_suit:
                            product = line.product_template_id.bom_ids[0].product_tmpl_id
                            product.write(product_data)
                        else:
                            product = self.env['product.template'].create(product_data)
                        line.write({
                            'product_id':
                                product.with_context(active_test=False
                                                    ).product_variant_ids[0].id
                        })
                        bom_data = {
                            'product_tmpl_id': product.id,
                            'product_qty': line.product_uom_qty,
                            'active': False,
                            'bom_line_ids': [(5, )] + [
                                (
                                    0, 0, {
                                        'ons_body_part_id': detail.body_part_id.id,
                                        'product_id': detail.product_id.id,
                                        'product_qty': detail.product_qty,
                                        'product_uom_id': detail.product_id.uom_id.id,
                                        'ons_note': detail.note,
                                    }
                                ) for detail in line.ons_detail_ids.
                                filtered(lambda r: not r.display_type)
                            ],
                        }
                        if line.product_template_id.bom_ids and not line.product_template_id.ons_is_suit:
                            line.product_template_id.bom_ids[0].write(bom_data)
                        else:
                            self.env['mrp.bom'].create(bom_data)

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for so in self:
            for line in so.order_line:
                if line.ons_detail_ids:
                    mo_form = Form(self.env['mrp.production'])
                    mo_form.product_id = line.product_id
                    mo_form.bom_id = line.product_template_id.with_context(
                        active_test=False
                    ).bom_ids[0]
                    mo_form.product_qty = line.product_uom_qty
                    mo_form.product_uom_id = line.product_uom
                    mo_form.ons_sale_order_line_id = line
                    mo_form.ons_note = line.ons_note
                    mo_form.ons_measure_id = line.ons_measure_id
                    mo_form.save()
        return res

    def ons_action_view_mrp_production(self):
        if not self.ons_mrp_production_count:
            return
        # if self.ons_mrp_production_count == 1:
        #     action = self.env.ref('ons_cust_sftech.mrp_production_sale_action_form').read()[0]
        # if self.ons_mrp_production_count > 1:
        action = self.env.ref('ons_cust_sftech.mrp_production_sale_action_tree'
                             ).read()[0]
        action['domain'] = [('id', 'in', self.ons_mrp_production_ids.ids)]
        return action

    @api.depends('ons_mrp_production_ids')
    def _compute_ons_mrp_production_count(self):
        for so in self:
            so.ons_mrp_production_count = len(so.ons_mrp_production_ids)

    def _compute_ons_picking_state(self):
        for so in self:
            if not so.picking_ids:
                so.ons_picking_state = 'no_picking'
                continue
            if len(so.picking_ids) == len(
                so.picking_ids.filtered(lambda x: x.state == so.picking_ids[0].state)
            ):
                so.ons_picking_state = so.picking_ids[0].state
                continue
            so.ons_picking_state = 'mix'

    def ons_reset(self):
        for so in self:
            for inv in so.invoice_ids:
                if inv.payment_state != 'not_paid':
                    raise UserError(
                        'Une facture a déjà été payée; impossible d\'annuler !'
                    )

            for mo in so.ons_mrp_production_ids:
                if mo.state == 'done':
                    raise UserError(
                        'Un ordre de production est déjà terminé; impossible d\'annuler !'
                    )

            for inv in so.invoice_ids:
                inv.button_cancel()

            for mo in so.ons_mrp_production_ids:
                mo.action_cancel()

            so.action_cancel()
            so.action_draft()
