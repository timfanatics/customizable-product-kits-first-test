from odoo import models, fields,api


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'
    is_bom_extracted = fields.Boolean("Is BOM Extracted", default=False)

    sequence = fields.Integer(string="Sequence", default=2)

    def extract_product_bom(self):
        if self.order_line:
            so_line_seq = 2
            for so_line in self.order_line:
                new_so_line_ids = []
                so_line.sequence = so_line_seq
                new_sol_lines, so_line_seq = self.is_bom_kit_prod(so_line.product_id, so_line, new_so_line_ids,
                                                                  so_line_seq, bom_qty=1)
                pass

                # list product with no BOM at the end
                if not new_so_line_ids:
                    self.env['sale.order.line'].browse(so_line.id).write({'sequence': 1000})
                else:
                    # unlink so with
                    so_line.unlink()

        self.calculate_kit_total_value()

    @api.onchange('order_line')
    def onchange_order_line(self):
        self.calculate_kit_total_value()

    def calculate_kit_total_value(self):
        bom_heads = self.order_line.filtered(lambda line:line.is_bom_head).sorted(key=lambda r: r.sequence,reverse=True)
        for rec in bom_heads:
            unit_price = sum(self.order_line.filtered(lambda line:line.parent_bom_product_id.id == rec.product_id.id and line.product_id.id != rec.product_id.id).mapped('price_subtotal'))
            rec.write({
                'price_unit':unit_price
            })

    def is_bom_kit_prod(self, product_id, so_line, new_so_line_ids, sequence, bom_qty):
        bom_id = self._get_bom(product_id)
        if bom_id:
            line_sect_id = self.create_so_line_section(sequence, product_id,so_line)
            sequence = sequence + 1
            if bom_id[0].bom_line_ids:
                self.is_bom_extracted = True
                for bom_line in bom_id.bom_line_ids:
                    print('line section', line_sect_id.name)
                    new_so_line = self.create_so_line_product(bom_line, so_line, sequence,product_id)

                    if new_so_line:
                        new_so_line_ids.append(new_so_line)
                    abc, sequence = self.is_bom_kit_prod(product_id=bom_line.product_id, so_line=so_line,
                                                         new_so_line_ids=new_so_line_ids, sequence=sequence,
                                                         bom_qty=bom_line.product_qty)
                    sequence = sequence + 1
            return new_so_line_ids, sequence
        else:
            return False, sequence

    def create_so_line_product(self, bom_line, so_line, sequence,head_product_id):

        bom_id = self._get_bom(bom_line.product_id)
        if bom_id:
            return False
        head_kit_prod_id = self._get_bom_service_product(head_product_id)
        order_line_vals = {
            'product_id': bom_line.product_id.id,
            'product_uom_qty': bom_line.product_qty * so_line.product_uom_qty,
            'price_unit': 0,
            'sequence': sequence,
            'order_id': self.id,
            'is_sub_product': True,
            'parent_bom_product_id': head_kit_prod_id.id
        }
        new_so_id = self.env['sale.order.line'].sudo().create(order_line_vals)

        price = new_so_id.with_company(new_so_id.company_id)._get_display_price()
        unit_price = new_so_id.product_id._get_tax_included_unit_price(
                    new_so_id.company_id,
                    new_so_id.order_id.currency_id,
                    new_so_id.order_id.date_order,
                    'sale',
                    fiscal_position=new_so_id.order_id.fiscal_position_id,
                    product_price_unit=price,
                    product_currency=new_so_id.currency_id
                )
        new_so_id.price_unit = unit_price
        return new_so_id

    def create_so_line_section(self, sequence, product_id,so_line):
        service_product = self._get_bom_service_product(product_id)
        parent_service_product = self._get_bom_service_product(so_line.product_id)
        line_section = {
            'product_id': service_product.id,
            'product_uom_qty': 1,
            'price_unit': 0,
            'is_bom_head': True,
            'sequence': sequence - 1,
            'order_id': self.id,
            'parent_bom_product_id': parent_service_product.id
        }
        line_sect_id = self.env['sale.order.line'].sudo().create(line_section)
        return line_sect_id

    def _get_bom(self, product_id):
        bom_id = self.env['mrp.bom'].sudo().search([('product_id', '=', product_id.id), ('type', '=', 'phantom')])
        if not bom_id:
            bom_id = self.env['mrp.bom'].sudo().search(
                [('product_tmpl_id', '=', product_id.product_tmpl_id.id), ('type', '=', 'phantom')])

        return bom_id

    def _get_bom_service_product(self, bom_product_id):
        product_name = bom_product_id.name + " KIT"
        product = self.env['product.product'].search([('name', '=', product_name), ('detailed_type', '=', 'service')])
        if not product:
            product_vals = {
                'name': product_name,
                'detailed_type': 'service',
                'categ_id': bom_product_id.categ_id.id,
            }
            product = self.env['product.product'].create(product_vals)

        return product


class SaleOrderInlineInherit(models.Model):
    _inherit = 'sale.order.line'
    is_bom_head = fields.Boolean()
    is_sub_product = fields.Boolean()
    parent_bom_product_id = fields.Many2one('product.product')

    # @api.onchange('order_line','order_line.product_id','order_line.price_unit','order_line.product_uom_qty')
    # def _onchange_line(self):
    #     self.calculate_kit_total_value()


    # @api.onchange('product_id')
    # def _onchange_product_id_warning(self):
    #     res = super(SaleOrderInlineInherit,self)._onchange_product_id_warning()
    #     self.order_id.calculate_kit_total_value()
    #     return res
    #
    # @api.onchange('price_unit')
    # def _onchange_unit_price(self):
    #     self.order_id.calculate_kit_total_value()
    # @api.onchange('product_uom_qty')
    # def _onchange_unit_price(self):
    #     self.order_id.calculate_kit_total_value()


    # def write(self, vals):
    #     res = super(SaleOrderInlineInherit,self).write(vals)
    #
    #     if 'price_unit' in vals or 'product_uom_qty' in vals or 'product_id' in vals:
    #         self.order_id.calculate_kit_total_value()
    #
    #     return res

    # @api.onchange('price_subtotal')
    # def _onchange_unit_price(self):
    #     self.order_id.calculate_kit_total_value()
    # @api.onchange('product_uom_qty')
    # def _onchange_unit_price(self):
    #     self.order_id.calculate_kit_total_value()