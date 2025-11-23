from odoo import models, api

class PDFMakerUtil(models.AbstractModel):
    _name = 'pdfmake.util'
    _description = 'Utilidades para PDFMake'

    @api.model
    def create_simple_document(self, content, styles=None, header=None, footer=None):
        """
        Crea una definición de documento simple
        """
        doc_definition = {
            'content': content,
            'styles': styles or {},
            'defaultStyle': {
                'font': 'Roboto',
                'fontSize': 10,
            }
        }
        
        if header:
            doc_definition['header'] = header
            
        if footer:
            doc_definition['footer'] = footer
            
        return doc_definition

    @api.model
    def create_table(self, body, widths=None, header_rows=0):
        """
        Crea definición de tabla
        """
        table_def = {
            'table': {
                'body': body
            }
        }
        
        if widths:
            table_def['table']['widths'] = widths
            
        if header_rows:
            table_def['table']['headerRows'] = header_rows
            
        return table_def

    @api.model
    def create_table_from_records(self, records, fields, headers=None):
        """
        Crea tabla a partir de registros Odoo
        """
        if headers is None:
            headers = []
            for field in fields:
                field_obj = records._fields[field]
                headers.append(field_obj.string or field)
            
        table_body = [headers]
        
        for record in records:
            row = []
            for field in fields:
                value = getattr(record, field)
                # Convertir según el tipo de campo
                if hasattr(value, 'display_name'):
                    row.append(value.display_name)
                elif isinstance(value, bool):
                    row.append('Sí' if value else 'No')
                elif isinstance(value, (list, tuple)):
                    row.append(', '.join(str(item) for item in value))
                else:
                    row.append(str(value) if value else '')
            table_body.append(row)
            
        return self.create_table(table_body, header_rows=1)