# -*- coding: utf-8 -*-
#
#
#    Author: Nicolas Bessi
#    Copyright 2013 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
import datetime
from openerp import models, fields, api


class SaleOrderLine(models.Model):

    """Adds two exception functions to be called by the sale_exceptions module.

    The first one will ensure that an order line can be delivered on the
    delivery date, if the related product is in MTS. Validation is done by
    using the shop related to the sales order line location and using the line
    delay.
    The second one will raise a sales exception if the current SO will break an
    order already placed in future

    """

    _inherit = "sale.order.line"

    @api.one
    def _compute_line_delivery_date(self):
        date_order = self.order_id.date_order
        date_order = fields.Date.from_string(date_order)
        # delay is a float, that is perfectly supported by timedelta
        return date_order + datetime.timedelta(days=self.delay)

    @api.multi
    def _get_line_location(self):
        return self.order_id.shop_id.warehouse_id.lot_stock_id.id

    @api.one
    def can_command_at_delivery_date(self):
        """Predicate that checks whether a SO line can be delivered at delivery
        date.

        Delivery date is computed using date of the order + line delay.
        Location is taken from the shop linked to the line

        :return: True if line can be delivered on time

        """
        if not self.product_id or self.type != 'make_to_stock':
            return True
        delivery_date = self._compute_line_delivery_date()[0]
        delivery_date = fields.Datetime.to_string(delivery_date)
        ctx = {
            'to_date': delivery_date,
            'location': self._get_line_location(),
            'compute_child': True,
            }
        # Virtual qty is made on all childs of chosen location
        prod_for_virtual_qty = (self.product_id
                                .with_context(ctx)
                                .virtual_available)
        if prod_for_virtual_qty < self.product_uom_qty:
            return False
        return True

    @api.model
    def _get_states(self):
        return ('waiting', 'confirmed', 'assigned')

    @api.model
    def _get_affected_dates(self, location_id, product_id, delivery_date):
        """Determine future dates where virtual stock has to be checked.

        It will only look for stock move that pass by location_id.
        If your stock location have children or you have configured automated
        stock action
        they must pass by the location related to SO line, else the will be
        ignored

        :param location_id: location id to be checked
        :param product_id: product id te be checked

        :return: list of dates to be checked

        """
        cr = self._cr
        sql = ("SELECT date FROM stock_move"
               "  WHERE state IN %s"
               "   AND date > %s"
               "   AND product_id = %s"
               "   AND location_id = %s")
        cr.execute(sql, (self._get_states(),
                         delivery_date,
                         product_id,
                         location_id))
        return (row[0] for row in cr.fetchall())

    @api.one
    def future_orders_are_affected(self):
        """Predicate function that is a naive workaround for the lack of stock
        reservation.

        This can be a performance killer, you should not use it
        if you have constantly a lot of running Orders

        :return: True if future order are affected by current command line
        """
        if not self.product_id or not self.type == 'make_to_stock':
            return False
        delivery_date = self._compute_line_delivery_date()[0]
        delivery_date = fields.Datetime.to_string(delivery_date)
        location_id = self._get_line_location()
        ctx = {
            'location': location_id,
            'compute_child': True,
            }
        # Virtual qty is made on all childs of chosen location
        dates = self._get_affected_dates(location_id, self.product_id.id,
                                         delivery_date)
        for aff_date in dates:
            ctx['to_date'] = aff_date
            prod_for_virtual_qty = (self.product_id
                                    .with_context(ctx)
                                    .virtual_available)
            if prod_for_virtual_qty < self.product_uom_qty:
                return True
        return False
