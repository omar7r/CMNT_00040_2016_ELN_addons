# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Comunitea All Rights Reserved
#    $Jesús Ventosinos Mayor <jesus@comunitea.com>$
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
from openerp import models, fields, api


class AccountAnalyticJournal(models.Model):

    _inherit = 'account.analytic.journal'

    analytic_cost_journal = fields.Many2one('account.analytic.journal',
                                            'Analytic cost journal')


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.multi
    def invoice_validate(self):
        t_uom = self.env['product.uom']
        product_tmpl_obj = self.env['product.template']
        for invoice in self:
            if invoice.type not in ('out_invoice', 'out_refund'):
                continue
            company_currency = self.company_id.currency_id
            currency = self.currency_id.with_context(date=self.date_invoice)
            sign = -1 if self.type == 'out_invoice' else 1
            for analytic_move in invoice.mapped(
                    'move_id.line_id.analytic_lines'):
                if not analytic_move.product_id:
                    continue
                from_unit = analytic_move.product_uom_id.id
                product_unit = analytic_move.product_id.uom_id.id
                uom_qty = analytic_move.unit_amount
                if from_unit != product_unit:
                    uom_qty = t_uom._compute_qty(from_unit,
                                                 analytic_move.unit_amount,
                                                 product_unit)
                price_unit = 0
                quant_qty = 0
                if analytic_move.product_id.type != 'service':
                    for picking_id in self.picking_ids:
                        for move_line in picking_id.move_lines:
                            if move_line.product_id == analytic_move.product_id:
                                for quant in move_line.quant_ids:
                                    if quant_qty < 0:
                                        continue
                                    price_unit += quant.cost * quant.qty
                                    quant_qty += quant.qty
                if quant_qty:
                    price_unit = price_unit / quant_qty
                if not price_unit:
                    date = self.date_invoice
                    price_unit = product_tmpl_obj.get_history_price(analytic_move.product_id.product_tmpl_id.id, 
                                                                    self.company_id.id, 
                                                                    date=date) 
                price_unit = price_unit or analytic_move.product_id.standard_price
                amount = currency.compute(
                    price_unit *
                    uom_qty, company_currency) * sign
                if analytic_move.journal_id.analytic_cost_journal:
                    analytic_move.copy(
                        {'journal_id':
                         analytic_move.journal_id.analytic_cost_journal.id,
                         'amount': amount})
        return super(AccountInvoice, self).invoice_validate()
