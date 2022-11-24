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
        if vals.get('name', 'New') == 'New' and self.env.context.get('set_purchase_order_name',True):
            seq_date = None
            if 'date_order' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))
            vals['name'] = self_comp.env['ir.sequence'].with_context(dynamic_prefix_fields=vals).next_by_code(
                'purchase.order', sequence_date=seq_date) or '/'
        return super(PurchaseOrder, self).create(vals)


    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for order in self:
            if order.name == '/':
                self_comp = self.with_company(order.company_id)
                seq_date = None
                if order.date_order:
                    seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(order.date_order))
                dynamic_prefix_fields = order._build_order_dynamic_prefix_fields()
                order.name = self_comp.env['ir.sequence'].with_context(dynamic_prefix_fields=dynamic_prefix_fields).next_by_code('purchase.order',sequence_date=seq_date) or '/'
        return res

    def _build_order_dynamic_prefix_fields(self):
        self.ensure_one()
        vals = {}
        for field_name,_ in self._fields.items():
            vals.update({field_name:getattr(self,field_name)})
        return vals

