# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductSetLine(models.Model):
    _inherit = 'product.set.line'

    product_id = fields.Many2many(
        'product.product', domain=[('sale_ok', '=', True)],
        string='Variant', required=False)
    product_template_id = fields.Many2one(
        'product.template',
        string='Product',
        required=True,
    )
