from odoo import models, fields, api


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    def extract_product_bom(self):
        """
        This product will extract bom of all so lines, for whom bom is not already extracted, and will compute the value of parent/sections/service products
        :return:
        :rtype:
        """
        so_line_seq = 2
        # getting last sequence before sequence greater than 999, that is the number for product, which were part of orignal so and didn' have bom, i.e with empty section
        so_lines = self.order_line.filtered(lambda line:line.sequence<999)
        if so_lines:
            so_line_seq = so_lines[-1].sequence+1
        for so_line in self.order_line:
            # Extraction KIT type BOMs of SO Lines which have not been previously extracted, and also not of type line_section
            if not so_line.is_bom_extracted and so_line.display_type != 'line_section':
                new_so_line_ids = []
                # Calling this method to recursively check for sub kits
                self.is_bom_kit_prod(so_line.product_id,so_line.product_uom_qty, new_so_line_ids, so_line_seq)
                # list product with no BOM at the end, in a separate empty section
                if not new_so_line_ids and not so_line.is_bom_extracted:
                    so_line.write({'sequence': 1000})
                else:
                    so_line.unlink()
        # Adding an empty section only if there are some product in so_line, which doesn't have any boms
        if not any(self.order_line.filtered(lambda line: line.is_empty_section)) and any(self.order_line.filtered(lambda line: line.sequence>999 and not line.is_sub_product)):
            self.env['sale.order.line'].sudo().create({
                'display_type': 'line_section',
                'is_empty_section':True,
                'name': ' ',
                'sequence': 999,
                'order_id': self.id
            })


        # self.recompute_kit_qty()
        self.calculate_kit_total_value()

    def is_bom_kit_prod(self, product_id,qty_required, new_so_line_ids, sequence, parent_line_id=False,bom_line_id=False):
        """
        This method calls itself recursively to extract kit type bom and subkits
        :param product_id: product to check for bom and sub boms
        :type product_id:
        :param qty_required: qty required to add into the so lines for kit products, it will multiple this qty with the bom line qty
        :type qty_required:
        :param new_so_line_ids: so lines generated from bom and sub boms
        :type new_so_line_ids:
        :param sequence: so lines are handled using sequence
        :type sequence:
        :param parent_line_id: Parent product of the subkit or sub products of a kit
        :type parent_line_id:
        :return: will return the current sequence
        :rtype:
        """
        bom_id = self._get_bom(product_id)
        if bom_id:
            parent_line_id = self.create_so_line_section(sequence, product_id,parent_line_id,bom_line_id)
            sequence = sequence + 1
            for bom_line in bom_id.bom_line_ids:
                new_so_line = self.create_so_line_product(bom_line, qty_required, sequence, parent_line_id)
                if new_so_line:
                    new_so_line_ids.append(new_so_line)
                sequence = self.is_bom_kit_prod(product_id=bom_line.product_id,qty_required=bom_line.product_qty*qty_required, new_so_line_ids=new_so_line_ids, sequence=sequence,parent_line_id=parent_line_id,bom_line_id=bom_line.id)
                sequence = sequence + 1
            return sequence
        else:
            return sequence

    def create_so_line_product(self, bom_line, qty_required, sequence, parent_line_id=False):
        """
        this method will add a new line in so extracted from the BOM
        :param bom_line:
        :type bom_line: bom line current extracted
        :param qty_required:
        :type qty_required: qty required to for bom line product, this qty will be multiplied by the qty configured in the bom
        :param sequence:
        :type sequence: sequence to where this line should be placed in so lines
        :param parent_line_id:
        :type parent_line_id: current head of the line
        :return:
        :rtype:
        """
        bom_id = self._get_bom(bom_line.product_id)
        if bom_id:
            return False
        order_line_vals = {
            'product_id': bom_line.product_id.id,
            'product_uom_qty': bom_line.product_qty * qty_required,
            'price_unit': 0,
            'sequence': sequence,
            'order_id': self.id,
            'is_bom_extracted': True,
            'is_sub_product': True,
            # 'parent_bom_product_id': head_kit_prod_id.id,
            'bom_line_id': bom_line.id,
            'parent_line_id': parent_line_id,
        }
        new_so_id = self.env['sale.order.line'].sudo().create(order_line_vals)
        # Calculating price from pricelist
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

    def create_so_line_section(self, sequence, product_id,parent_line_id=False,bom_line_id=False):
        """
        This product creates a new parent/section/service product for all it's subkit or sub products of a kit
        :param sequence: ver important parameters, it will place the parent exactly before it's child
        :type sequence:
        :param product_id: product_id/parent  product/ kit/subkit product for which we are going to create a new parent/section/service product
        :type product_id:
        :param parent_line_id: parent line/parent product line of current paretn, it will be false for the very first product.
        :type parent_line_id:
        :return:
        :rtype:
        """
        # The logic here is to create a new service product for the products that are not of type kit and doesn't have a service product already
        service_product = self._get_bom_service_product(product_id)
        line_section = {
            'product_id': service_product.id,
            'product_uom_qty': 1,
            'price_unit': 0,
            'is_bom_head': True,
            'is_bom_extracted': True,
            'sequence': sequence - 1,
            'order_id': self.id,
            'parent_line_id': parent_line_id,
            'bom_line_id':bom_line_id,
        }
        parent_line_id = self.env['sale.order.line'].sudo().create(line_section)
        return parent_line_id.id

    def _get_bom(self, product_id):
        bom_id = self.env['mrp.bom'].sudo().search([('product_id', '=', product_id.id), ('type', '=', 'phantom')])
        if not bom_id:
            bom_id = self.env['mrp.bom'].sudo().search(
                [('product_tmpl_id', '=', product_id.product_tmpl_id.id), ('type', '=', 'phantom')])
        return bom_id

    def _get_bom_service_product(self, bom_product_id):
        product_name = bom_product_id.name + " KIT"
        product = self.env['product.product'].search([('name', '=', product_name), ('detailed_type', '=', 'service'),('active','in',(True,False))])
        if not product:
            product_vals = {
                'name': product_name,
                'detailed_type': 'service',
                'categ_id': bom_product_id.categ_id.id,
                'active': False,
            }
            product = self.env['product.product'].create(product_vals)
        # Just archiving this product because we don't need to
        elif any(product.filtered(lambda x:x.active)):
            for rec in product.filtered(lambda x:not x.active):
                rec.active = False

        return product[0]

    @api.onchange('order_line')
    def onchange_order_line(self):
        '''
        This method will calculate total value of sections/service products and sub_kits/sub_products quantity, iff any the line changes triggers
        :return:
        :rtype:
        '''
        self.ensure_one()
        bom_head = self.order_line.filtered(lambda line: line.is_current_line_head)
        if bom_head:
            for head in bom_head:
                head._origin.is_current_line_head = False
            self.recompute_kit_qty(bom_head[0],bom_head[0].product_uom_qty)
        self.calculate_kit_total_value()

    def recompute_kit_qty(self,bom_head,qty_required):
        """
        This metho will recuresively recompute quantites of subkits and subproducts, it will not recompute for the sub kits and sections
        :param bom_head:
        :type bom_head:
        :return:
        :rtype:
        """
        # qty_required = bom_head.product_uom_qty
        sub_kit_products = self.order_line.filtered(lambda x:x.parent_line_id.id == bom_head._origin.id)
        for line in sub_kit_products:
            qty = line.bom_line_id.product_qty * qty_required
            if not line.is_sub_kit:
                line.update({
                    'product_uom_qty':qty
                })
            self.recompute_kit_qty(line,qty)

    def calculate_kit_total_value(self):
        """
        This method will recompute total value of sectoins/sub kits as they are based on the total price of their child subkits/subproducts
        :return:
        :rtype:
        """
        bom_heads = self.order_line.filtered(lambda line: line.is_bom_head).sorted(key=lambda r: r.sequence, reverse=True)
        for rec in bom_heads:
            unit_price = sum(self.order_line.filtered(lambda line: line.parent_line_id.id == rec._origin.id).mapped('price_subtotal'))
            rec.write({
                'price_unit': unit_price,
                'price_subtotal': unit_price
            })

    @api.depends('order_line.price_subtotal', 'order_line.price_tax', 'order_line.price_total')
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        for order in self:
            # if order is an order with bom extracted than we have to recalculate the totals
            is_so_with_bom = any(order.order_line.filtered(lambda x: x.is_bom_head))
            if is_so_with_bom:
                # Calculating total based on: parents only or products without bom or newly added products
                order_lines = order._get_lines_for_total()
                order.amount_untaxed = sum(order_lines.mapped('price_subtotal'))
                order.amount_total = sum(order_lines.mapped('price_total'))
                order.amount_tax = sum(order_lines.mapped('price_tax'))
            else:
                super(SaleOrderInherit,self)._compute_amounts()
        pass
    def _get_lines_for_total(self):
        order_lines = self.order_line.filtered(
            lambda x: not x.display_type and x.is_bom_head and not x.parent_line_id or x.sequence > 999)
        return order_lines
    @api.depends('order_line.tax_id', 'order_line.price_unit', 'amount_total', 'amount_untaxed')
    def _compute_tax_totals(self):
        for order in self:
            # if order is an order with bom extracted than we have to recalculate the totals
            is_so_with_bom = any(order.order_line.filtered(lambda x: x.is_bom_head))
            if is_so_with_bom:
                # Calculating total based on: parents only or products without bom or newly added products
                order_lines = order._get_lines_for_total()
                # order_lines = order.order_line.filtered(lambda x: not x.display_type)
                tax_totals = self.env['account.tax']._prepare_tax_totals(
                    [x._convert_to_tax_base_line_dict() for x in order_lines],
                    order.currency_id,
                )
                order.tax_totals = tax_totals
            else:
                super(SaleOrderInherit,self)._compute_tax_totals()
            pass
