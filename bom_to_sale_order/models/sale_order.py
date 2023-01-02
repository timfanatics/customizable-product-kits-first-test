from odoo import models, fields


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
                # qty_count = so_line.product_uom_qty
                # self.env['sale.order.line'].browse(so_line.id).write({'sequence': so_line_seq})
                new_sol_lines, so_line_seq = self.is_bom_kit_prod(so_line.product_id, so_line, new_so_line_ids,
                                                                  so_line_seq)
                pass

                # calculate qty of new (BOM) lines
                # for new_line in new_so_line_ids:
                #     qty_count += new_line.product_uom_qty

                # bom_line_section = self.env['sale.order.line'].sudo().search(
                #     [('display_type', '=', 'line_section'), ('name', '=', so_line.product_id.name),
                #      ('order_id', '=', self.id),
                #      ('product_id', '=', False)])
                # bom_line_section.write({'name': str(so_line.product_id.name) + ' (' + str(qty_count) + ')'})
                # list product with no BOM at the end
                if not new_so_line_ids:
                    self.env['sale.order.line'].browse(so_line.id).write({'sequence': 1000})
                # so_line_seq += 2

            # adding line section for products without BOM
            line_section = {
                'name': ' ',
                'display_type': 'line_section',
                'sequence': 999,
                'order_id': self.id,
            }
            self.env['sale.order.line'].sudo().create(line_section)

    def is_bom_kit_prod(self, product_id, so_line, new_so_line_ids, sequence):
        bom_id = self._get_bom(product_id)
        if bom_id:
            self.create_so_line_section(product_id.name, sequence)
            sequence = sequence + 1
            if bom_id[0].bom_line_ids:
                self.is_bom_extracted = True
                for bom_line in bom_id.bom_line_ids:
                    new_so_line = self.create_so_line_product(bom_line, so_line, sequence)
                    if new_so_line:
                        new_so_line_ids.append(new_so_line)
                    abc, sequence = self.is_bom_kit_prod(product_id=bom_line.product_id, so_line=so_line,
                                                         new_so_line_ids=new_so_line_ids, sequence=sequence)
                    sequence = sequence + 1
            return new_so_line_ids, sequence
        else:
            return False, sequence

    def create_so_line_product(self, bom_line, so_line, sequence):

        bom_id = self._get_bom(bom_line.product_id)
        if bom_id:
            return False
            # qty = bom_line.product_qty * so_line.product_uom_qty
            # new_section_name = str(bom_line.product_id.name) + ' (' + str(qty) + ')'
            # so_line_sect = self.env['sale.order.line'].sudo().search(
            #     [('display_type', '=', 'line_section'), ('name', '=', bom_line.product_id.name),
            #      ('order_id', '=', self.id), ('product_id', '=', False)])
            # if so_line_sect:
            #     so_line_sect[0].write({'name': new_section_name})

            # print(bom_line.product_id.name, qty)
            # return False
        order_line_vals = {
            'product_id': bom_line.product_id.id,
            'product_uom_qty': bom_line.product_qty * so_line.product_uom_qty,
            'price_unit': bom_line.product_id.list_price,
            'sequence': sequence,
            'order_id': self.id,
        }
        new_so_id = self.env['sale.order.line'].sudo().create(order_line_vals)
        return new_so_id

    def create_so_line_section(self, section_name, sequence):
        line_section = {
            'name': section_name,
            'display_type': 'line_section',
            'sequence': sequence - 1,
            'order_id': self.id,
        }
        line_sect_id = self.env['sale.order.line'].sudo().create(line_section)
        return line_sect_id

    def _get_bom(self, product_id):
        bom_id = self.env['mrp.bom'].sudo().search([('product_id', '=', product_id.id), ('type', '=', 'phantom')])
        if not bom_id:
            bom_id = self.env['mrp.bom'].sudo().search(
                [('product_tmpl_id', '=', product_id.product_tmpl_id.id), ('type', '=', 'phantom')])

        return bom_id
