# -*- coding: utf-8 -*- 

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.model
    def create(self, vals):
        """ Inherit this method to add the dynamic prefix in the call of the sequence so that any dynamic sequence configuration can be detected"""
        company_id = vals.get('company_id', self.default_get(['company_id'])['company_id'])
        # Ensures default picking type and currency are taken from the right company.
        self_comp = self.with_company(company_id)
        if vals.get('name', 'New') == 'New':
            seq_date = None
            if 'date_order' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))
            vals['name'] = self_comp.env['ir.sequence'].with_context(dynamic_prefix_fields=vals).next_by_code(
                'purchase.order', sequence_date=seq_date) or '/'
        return super(PurchaseOrder, self).create(vals)
