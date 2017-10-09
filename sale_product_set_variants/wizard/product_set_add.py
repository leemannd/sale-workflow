# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class ProductSetAd(models.TransientModel):
    _inherit = 'product.set.add'

    product_set_id = fields.Many2one(
        'product.set', 'Product set', required=True)
    set_line_ids = fields.One2many(
        'wizard.product.set.line',
        'wiz_id',
        string='Products',
    )

    @api.onchange('product_set_id')
    def _onchange_product_set_id(self):
        wiz_line = self.env['wizard.product.set.line']
        if self.product_set_id:
            for line in self.product_set_id.set_line_ids:
                self.set_line_ids |= wiz_line.create({
                    'source_line_id': line.id,
                    'product_id': line.product_id.id,
                    'quantity': line.quantity,
                    'product_set_id': line.product_set_id.id,
                    'product_template_id': line.product_template_id.id,
                    'sequence': line.sequence})

    @api.onchange('quantity')
    def _onchange_quantity(self):
        if self.quantity > 0:
            for line in self.set_line_ids:
                line.quantity = line.source_line_id.quantity * self.quantity
