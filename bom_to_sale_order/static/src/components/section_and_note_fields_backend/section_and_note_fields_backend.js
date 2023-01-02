/** @odoo-module **/
import { registry } from "@web/core/registry";
import { ListRenderer } from "@web/views/list/list_renderer";
import {SectionAndNoteListRenderer} from "@account/components/section_and_note_fields_backend/section_and_note_fields_backend"
import {SectionAndNoteFieldOne2Many} from "@account/components/section_and_note_fields_backend/section_and_note_fields_backend"

export class ExpandListRenderer extends SectionAndNoteListRenderer {
    setup() {
        super.setup();
    }



    getSectionColumns(columns) {
        const sectionCols = super.getSectionColumns(columns);
        return sectionCols.map((col) => {
            if (col.name === this.titleField) {
                return { ...col, colspan: columns.length - sectionCols.length};
            } else {
                return { ...col };
            }
        });
    }



    async onClickExpandCollapse(ev,record) {
        debugger;


        const currentButton = $(ev.target)
        if(currentButton.hasClass('fa-chevron-up')){
            currentButton.removeClass('fa-chevron-up').addClass('fa-chevron-down');
        }
        else{
            currentButton.removeClass('fa-chevron-down').addClass('fa-chevron-up');
        }
        var index = currentButton.closest('td').parent().index();
        if(!index){
            index = 0;
        }
        else{
            index = parseInt(index)
        }
        const t_rows = ev.currentTarget.closest('tbody').children
        for (var i = index+1 ; i < t_rows.length; i++) {
            const row = $(t_rows[i]);
            var height = row.clientHeight;
            var width = row.clientWidth;
            if(row.hasClass('o_is_false')){
                if(row.hasClass('d-none')){
                    row.removeClass('d-none');
                }
                else{
                    row.addClass('d-none');
                }
                console.log(row);
            }
            else{
                return false
            }
        }
    }
}

/*ExpandListRenderer.template = "bom_to_sale_order.ExpandListRenderer";*/
ExpandListRenderer.recordRowTemplate = "bom_to_sale_order.ExpandListRenderer.RecordRow";

export class SectionAndNoteFieldOne2ManyExpand extends SectionAndNoteFieldOne2Many {}
SectionAndNoteFieldOne2ManyExpand.components = {
    ...SectionAndNoteFieldOne2Many.components,
    ListRenderer: ExpandListRenderer,
};

registry.category("fields").add("section_and_note_one2many_expand", SectionAndNoteFieldOne2ManyExpand);