import logging
import subprocess
import sys
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def install_pdfmake(cr):
    """
    Instala la librería pdfmake usando pip
    """
    try:
        # Intentar importar para verificar si ya está instalado
        import pdfmake
        _logger.info("✓ PDFMake ya está instalado")
        return True
    except ImportError:
        _logger.info("Instalando PDFMake...")
        
        try:
            # Instalar pdfmake usando pip
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "pdfmake"
            ])
            _logger.info("✓ PDFMake instalado correctamente")
            return True
        except subprocess.CalledProcessError as e:
            _logger.error("✗ Error instalando PDFMake: %s", str(e))
            return False
        except Exception as e:
            _logger.error("✗ Error inesperado instalando PDFMake: %s", str(e))
            return False

def post_init_hook(cr, registry):
    """
    Hook que se ejecuta después de instalar el módulo
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    install_pdfmake(cr)