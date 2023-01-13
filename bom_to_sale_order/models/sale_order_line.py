from odoo import models, fields, api

class SaleOrderInlineInherit(models.Model):
    _inherit = 'sale.order.line'
    is_bom_head = fields.Boolean()
    is_sub_kit = fields.Boolean(compute="compute_is_sub_kit",store=True)
    is_sub_product = fields.Boolean()
    is_bom_extracted = fields.Boolean()
    # parent_bom_product_id = fields.Many2one('product.product')
    bom_line_id = fields.Many2one('mrp.bom.line')
    is_empty_section = fields.Boolean()

    # head_line_id = fields.Many2one('sale.order.line')

    parent_line_id = fields.Many2one('sale.order.line')
    is_current_line_head = fields.Boolean(default=False)
    # sub_kit_line_id = fields.Integer()

    # @api.onchange('product_uom_qty')
    # def _onchange_product_uom_qty(self):
    #     # sub_kit_lines = self.env['sale.order.line'].sudo().search([('parent_line_id', '=', self._origin.id)])
    #     sub_kit_lines = self.order_id.order_line.filtered(lambda x:x.parent_line_id.id == self._origin.id)
    #     qty_required = self.product_uom_qty
    #     for line in sub_kit_lines:
    #         bom_qty = line.bom_line_id.product_qty
    #         qty = bom_qty * qty_required
    #         line._origin.update({
    #             'product_uom_qty':qty
    #         })


    @api.depends('bom_line_id','bom_line_id.product_id')
    def compute_is_sub_kit(self):
        for rec in self:
            if rec.bom_line_id:
                is_sub_kit_line = rec.order_id._get_bom(rec.bom_line_id.product_id)
                if is_sub_kit_line:
                    rec._origin.is_sub_kit = True
                else:
                    rec._origin.is_sub_kit = False
            else:
                rec._origin.is_sub_kit = False
    @api.onchange('product_uom_qty')
    def _onchange_product_uom_qty(self):
        for rec in self:
            if rec._origin.is_bom_head:
                rec._origin.is_current_line_head = True
            else:
                rec._origin.is_current_line_head = False


    # @api.depends('product_id', 'product_uom', 'product_uom_qty')
    # def _compute_price_unit(self):
    #     for line in self:
    #         # not computing value for bom heads as they are getting their value from sub product/kits
    #         if not line.is_bom_head:
    #             super(SaleOrderInlineInherit,self)._compute_price_unit()

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        for line in self:
            # not computing value for bom heads as they are getting their value from sub product/kits
            if not line.is_bom_head:
                super(SaleOrderInlineInherit,self)._compute_amount()

    def _convert_to_tax_base_line_dict(self):
        res = super()._convert_to_tax_base_line_dict()
        # updating quantity to 1 for is_bom_head lines, this is to compute totals with qty, as bom heads are getting their value from sub product/kits
        if self.is_bom_head:
            res['quantity'] = 1
        return res