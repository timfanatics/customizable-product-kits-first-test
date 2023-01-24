odoo.define('bom_to_sale_order.salePortalProducts', function (require) {
  'use strict';

    const core = require('web.core');
    const publicWidget = require('web.public.widget');
    const _t = core._t;

    publicWidget.registry.salePortalProducts = publicWidget.Widget.extend({
        selector: '.o_portal_sale_sidebar',
        events: Object.assign({}, publicWidget.Widget.prototype.events, {
            'change .select_line_type': '_onDisplayTypeChanged',
        }),

        /**
         * @constructor
         */
        init: function () {
            const preventDoubleClick = handlerMethod => {
                return _.debounce(handlerMethod, 500, true);
            };
            this._super(...arguments);
            this._onDisplayTypeChanged();
        },

        _onDisplayTypeChanged: function(ev){
            const displayType = $('select#d_line_type option:selected').val()

//             $(ev.currentTarget).val();
            console.log("displayType",displayType);
            debugger;
            $('.sale_tbody tr').each(function() {
                if(!$(this).is('.bom_head, .sub_kit, .no_bom_product, .is-subtotal')){
                    if(displayType == "heads"){
                        $(this).addClass('d-none');
                    }
                    else{
                        $(this).removeClass('d-none');
                    }
                }
            });

        },

    });
    return publicWidget.registry.salePortalProducts;
});


/*odoo.define('bom_to_sale_order.salePortalProducts', function (require) {
'use strict';

const dom = require('web.dom');
var publicWidget = require('web.public.widget');
var PortalSidebar = require('portal.PortalSidebar');
var utils = require('web.utils');

publicWidget.registry.salePortalProducts = PortalSidebar.extend({
    selector: '.o_portal_sale_sidebar',
    events: {
        'click .o_portal_invoice_print': '_onPrintInvoice',
    },

    *//**
     * @override
     *//*
    start: function () {
        var def = this._super.apply(this, arguments);

        var $invoiceHtml = this.$el.find('iframe#invoice_html');
        var updateIframeSize = this._updateIframeSize.bind(this, $invoiceHtml);

        $(window).on('resize', updateIframeSize);

        var iframeDoc = $invoiceHtml[0].contentDocument || $invoiceHtml[0].contentWindow.document;
        if (iframeDoc.readyState === 'complete') {
            updateIframeSize();
        } else {
            $invoiceHtml.on('load', updateIframeSize);
        }

        return def;
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    *//**
     * Called when the iframe is loaded or the window is resized on customer portal.
     * The goal is to expand the iframe height to display the full report without scrollbar.
     *
     * @private
     * @param {object} $el: the iframe
     *//*
    _updateIframeSize: function ($el) {
        var $wrapwrap = $el.contents().find('div#wrapwrap');
        // Set it to 0 first to handle the case where scrollHeight is too big for its content.
        $el.height(0);
        $el.height($wrapwrap[0].scrollHeight);

        // scroll to the right place after iframe resize
        if (!utils.isValidAnchor(window.location.hash)) {
            return;
        }
        var $target = $(window.location.hash);
        if (!$target.length) {
            return;
        }
        dom.scrollTo($target[0], {duration: 0});
    },
    *//**
     * @private
     * @param {MouseEvent} ev
     *//*
    _onPrintInvoice: function (ev) {
        ev.preventDefault();
        var href = $(ev.currentTarget).attr('href');
        this._printIframeContent(href);
    },
});
});*/
