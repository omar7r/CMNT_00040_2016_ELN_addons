# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2014 Pexego Sistemas Informáticos All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import fields, osv

class cancel_intervention_request_wizard(osv.osv_memory):
    _name = "cancel.intervention.request.wizard"
    _columns = {
            'motivo': fields.text('Reason for cancellation', required=True),
                    }

    def close_confirm(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        if not ids:
            return
        wizards = self.pool.get('cancel.intervention.request.wizard').browse(cr, uid, ids, context)
        for wizard in wizards:
            self.pool.get('intervention.request').write(cr, uid, context['active_id'], {'state':'cancelled','motivo_cancelacion':wizard.motivo }, context)
        return {'type':'ir.actions.act_window_close'}
cancel_intervention_request_wizard()
