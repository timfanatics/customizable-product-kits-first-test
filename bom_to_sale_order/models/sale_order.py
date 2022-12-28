from odoo import models, fields


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'
    is_bom_extracted = fields.Boolean("Is BOM Extracted", default=False)

    def extract_product_bom(self):
        if self.order_line:
            so_line_seq = 2
            for so_line in self.order_line:
                self.is_bom_extracted = True
                new_so_line_ids = []
                qty_count = so_line.product_uom_qty
                self.env['sale.order.line'].browse(so_line.id).write({'sequence': so_line_seq})
                self.is_bom_kit_prod(so_line.product_id, so_line, new_so_line_ids)

                # calculate qty of new (BOM) lines
                for new_line in new_so_line_ids:
                    qty_count += new_line.product_uom_qty
                bom_line_section = self.env['sale.order.line'].sudo().search(
                    [('name', '=', so_line.product_id.name), ('order_id', '=', self.id)])
                bom_line_section.write({'name': str(so_line.product_id.name) + ' (' + str(qty_count) + ')'})
                # list product with no BOM at the end
                if not new_so_line_ids:
                    self.env['sale.order.line'].browse(so_line.id).write({'sequence': 1000})
                so_line_seq += 2

            # adding line section for products without BOM
            line_section = {
                'name': ' ',
                'display_type': 'line_section',
                'sequence': 999,
                'order_id': self.id,
            }
            self.env['sale.order.line'].sudo().create(line_section)

    def is_bom_kit_prod(self, product_id, so_line, new_so_line_ids):
        bom_id = self.env['mrp.bom'].sudo().search([('product_id', '=', product_id.id), ('type', '=', 'phantom')])
        if not bom_id:
            bom_id = self.env['mrp.bom'].sudo().search(
                [('product_tmpl_id', '=', product_id.product_tmpl_id.id), ('type', '=', 'phantom')])
        if bom_id:
            if bom_id[0].bom_line_ids:
                self.is_bom_extracted = True
                for bom_line in bom_id.bom_line_ids:
                    new_so_line = self.create_so_line(bom_line, so_line)
                    # if new_so_line:
                    #     new_so_line_ids.append(new_so_line)
                    new_so_line_ids.append(new_so_line)
                    self.is_bom_kit_prod(product_id=bom_line.product_id, so_line=so_line,
                                         new_so_line_ids=new_so_line_ids)
            return new_so_line_ids

    def create_so_line(self, bom_line, so_line):
        is_line_section = self.env['sale.order.line'].sudo().search(
            [('name', '=', so_line.product_id.name), ('order_id', '=', self.id)])
        if not is_line_section:
            line_section = {
                'name': so_line.product_id.name,
                'display_type': 'line_section',
                'sequence': so_line.sequence - 1,
                'order_id': self.id,
            }
            self.env['sale.order.line'].sudo().create(line_section)

        order_line_vals = {
            'product_id': bom_line.product_id.id,
            'product_uom_qty': bom_line.product_qty * so_line.product_uom_qty,
            'price_unit': bom_line.product_id.list_price,
            'sequence': so_line.sequence,
            'order_id': self.id,
        }
        new_so_id = self.env['sale.order.line'].sudo().create(order_line_vals)
        return new_so_id
