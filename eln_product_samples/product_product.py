# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>). All Rights Reserved.
#    
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import fields, orm
import openerp.addons.decimal_precision as dp


class product_template(orm.Model):

    def _get_product_samples(self, cr, uid, ids, field_name, arg, context):
        """
            Gets remaining samples checking sale order lines with its product and checkbox 'Sample?' check
        """
        res = {}
        qty = 0.0
        c = context.copy()
        wh_ids = self.pool.get('stock.warehouse').search(cr, uid, [])
        samp_ids = set()
        for wh in self.pool.get('stock.warehouse').browse(cr, uid, wh_ids, c):
            if wh.samples_loc_id:
                samp_ids.add(wh.samples_loc_id.id)
        samp_ids = list(samp_ids)
        c.update({'location': samp_ids, 'warehouse': False})
        for product in self.pool.get('product.template').browse(cr, uid, ids, context=c):
            qty += round(product.qty_available, 2)
            res[product.id] = qty
        return res

    _inherit = 'product.template'

    _columns = {
        'remaining_samples':fields.function(_get_product_samples, method=True, string='Samples', type='float', digits_compute=dp.get_precision('Product Unit of Measure'), help="Given Samples (in UoM)", readonly=True),
    }

