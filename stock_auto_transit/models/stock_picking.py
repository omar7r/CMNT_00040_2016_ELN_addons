# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def do_transfer(self):
        """
        When we finish a picking that takes the goods to a transit location
        The system will process automatically the chained picking to take the
        goods from the transit location to the destination location
        """
        res = super(StockPicking, self).do_transfer()
        pick2process_ids = set()
        su_move = self.env['stock.move'].sudo()  # Because of multicompany
        for pick in self:
            for move in pick.move_lines:
                if move.location_dest_id.usage == 'transit' and \
                        move.move_dest_id:
                    next_move = su_move.browse(move.move_dest_id.id)
                    pick2process_ids.add(next_move.picking_id.id)

        pick2process_ids = list(pick2process_ids)
        for pick_id in pick2process_ids:
            pick = self.sudo().browse(pick_id)  # Because of multicompany
            pick.do_prepare_partial()
            if pick.state != 'done':
                pick.do_transfer()
        return res
