# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from odoo.addons import decimal_precision as dp


class WizardProductSetLine(models.TransientModel):
    _name = 'wizard.product.set.line'
    _order = 'sequence'

    wiz_id = fields.Many2one(
        'product.set.add',
    )
    source_line_id = fields.Many2one(
        'product.set.line',
    )
    product_id = fields.Many2one(
        'product.product', domain=[('sale_ok', '=', True)],
        string='Product',
        default='source_line_id.product_id',)
    quantity = fields.Float(
        string='Quantity',
        digits=dp.get_precision('Product Unit of Measure'),
    )
    product_set_id = fields.Many2one(
        'product.set',
        string='Set',
        default='source_line_id.product_set_id',
    )
    product_template_id = fields.Many2one(
        'product.template',
        string='Product',
        required=True,
    )
    sequence = fields.Integer(
        string='Sequence',
        required=True,
        default=0,
    )
