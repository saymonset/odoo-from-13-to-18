import os
import logging
import tempfile
import base64
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.modules import get_module_path

_logger = logging.getLogger(__name__)

# Intentar importar pdfmake, pero no fallar si no está disponible
PDFMAKE_AVAILABLE = False
try:
    from pdfmake import PDFMake
    PDFMAKE_AVAILABLE = True
except ImportError:
    _logger.warning("PDFMake no está disponible. Se instalará automáticamente.")

class PDFPrinter(models.Model):
    _name = 'pdfmake.printer'
    _description = 'PDFMake Printer Service'

    name = fields.Char(string='Nombre', required=True, default='PDF Printer Service')
    use_local_fonts = fields.Boolean(
        string='Usar Fuentes Locales',
        default=True,
        help='Usar fuentes incluidas en el módulo'
    )
    pdfmake_available = fields.Boolean(
        string='PDFMake Disponible',
        compute='_compute_pdfmake_available',
        default=PDFMAKE_AVAILABLE
    )

    @api.depends()
    def _compute_pdfmake_available(self):
        """Calcula si PDFMake está disponible"""
        for record in self:
            record.pdfmake_available = PDFMAKE_AVAILABLE

    def _get_module_fonts_path(self):
        """Obtiene la ruta de las fuentes del módulo"""
        module_path = get_module_path('pdfmake_reports')
        if module_path:
            fonts_path = os.path.join(module_path, 'fonts')
            if os.path.exists(fonts_path):
                return fonts_path
        _logger.warning("No se pudo encontrar la ruta de fuentes del módulo")
        return None

    def _get_fonts_config(self):
        """Configuración de fuentes para PDFMake"""
        if self.use_local_fonts:
            fonts_path = self._get_module_fonts_path()
            if fonts_path:
                # Verificar qué archivos de fuentes existen realmente
                font_config = {}
                
                # Mapeo de estilos a archivos posibles
                font_files = {
                    "normal": ["Roboto-Regular.ttf", "Roboto-Black.ttf"],
                    "bold": ["Roboto-Bold.ttf"],
                    "italics": ["Roboto-Italic.ttf"],
                    "bolditalics": ["Roboto-BoldItalic.ttf", "Roboto-BlackItalic.ttf"]
                }
                
                for style, possible_files in font_files.items():
                    for font_file in possible_files:
                        font_path = os.path.join(fonts_path, font_file)
                        if os.path.exists(font_path):
                            font_config[style] = font_path
                            _logger.info("Usando fuente: %s para %s", font_file, style)
                            break
                    if style not in font_config:
                        _logger.warning("No se encontró fuente para estilo: %s", style)
                
                return {"Roboto": font_config}
            
            _logger.warning("No se pudieron encontrar fuentes locales, usando fuentes del sistema")
            self.use_local_fonts = False
        
        # Fuentes del sistema como fallback
        font_dir = '/usr/share/fonts/truetype/'
        return {
            "Roboto": {
                "normal": f"{font_dir}roboto/Roboto-Regular.ttf",
                "bold": f"{font_dir}roboto/Roboto-Medium.ttf", 
                "italics": f"{font_dir}roboto/Roboto-Italic.ttf",
                "bolditalics": f"{font_dir}roboto/Roboto-MediumItalic.ttf",
            }
        }

    def _validate_fonts(self):
        """Valida que existan los archivos de fuentes locales"""
        if not self.use_local_fonts:
            return True
            
        fonts_path = self._get_module_fonts_path()
        if not fonts_path:
            return False
            
        # Verificar que exista al menos una fuente
        required_fonts = [
            "Roboto-Regular.ttf", "Roboto-Black.ttf",  # Para normal
            "Roboto-Bold.ttf",                         # Para bold
        ]
        
        for font_file in required_fonts:
            font_path = os.path.join(fonts_path, font_file)
            if os.path.exists(font_path):
                return True
                
        _logger.warning("No se encontraron fuentes locales válidas")
        return False

    def action_install_pdfmake(self):
        """Acción para instalar PDFMake manualmente"""
        from .. import hooks
        success = hooks.install_pdfmake(self.env.cr)
        if success:
            # Recargar el estado de PDFMAKE_AVAILABLE
            global PDFMAKE_AVAILABLE
            try:
                from pdfmake import PDFMake
                PDFMAKE_AVAILABLE = True
                _logger.info("PDFMake instalado correctamente")
                
                # Mostrar notificación en Odoo 18
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Éxito',
                        'message': 'PDFMake se instaló correctamente. Por favor, actualice la página.',
                        'type': 'success',
                        'sticky': False,
                    }
                }
            except ImportError:
                PDFMAKE_AVAILABLE = False
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Error',
                        'message': 'No se pudo importar PDFMake después de la instalación.',
                        'type': 'error',
                        'sticky': True,
                    }
                }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'message': 'No se pudo instalar PDFMake. Revise los logs del servidor.',
                    'type': 'error',
                    'sticky': True,
                }
            }

    @api.model
    def create_pdf(self, doc_definition, options=None):
        """
        Crea un PDF y retorna el contenido como bytes
        """
        if not PDFMAKE_AVAILABLE:
            raise UserError(
                "PDFMake no está disponible. "
                "Por favor, instálelo manualmente desde la configuración del módulo o "
                "ejecute: pip install pdfmake"
            )
        
        if options is None:
            options = {}

        # Validar fuentes locales si están habilitadas
        if self.use_local_fonts and not self._validate_fonts():
            _logger.warning("Usando fuentes del sistema debido a fuentes locales faltantes")
            self.use_local_fonts = False

        fonts = self._get_fonts_config()
        
        # Verificar que tengamos al menos una fuente configurada
        if not fonts.get("Roboto"):
            raise UserError("No se pudieron cargar las fuentes para generar el PDF")
            
        printer = PDFMake(fonts)
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_path = tmp_file.name

        try:
            # Generar PDF
            printer.generate(doc_definition, tmp_path, options)
            
            # Leer y retornar contenido
            with open(tmp_path, 'rb') as f:
                pdf_content = f.read()
                
            return pdf_content
            
        except Exception as e:
            _logger.error("Error generando PDF: %s", str(e))
            raise UserError(f"Error generando PDF: {str(e)}")
        finally:
            # Limpiar archivo temporal
            import os
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def create_pdf_attachment(self, doc_definition, attachment_name, options=None, res_model=None, res_id=None):
        """
        Crea un PDF y lo guarda como attachment
        """
        pdf_content = self.create_pdf(doc_definition, options)
        
        attachment_vals = {
            'name': attachment_name,
            'type': 'binary',
            'datas': base64.b64encode(pdf_content),
            'mimetype': 'application/pdf',
            'res_model': res_model,
            'res_id': res_id,
        }
        
        return self.env['ir.attachment'].create(attachment_vals)

    @api.model
    def get_default_printer(self):
        """Obtiene el servicio de impresión por defecto"""
        return self.env.ref('pdfmake_reports.default_printer', raise_if_not_found=False)