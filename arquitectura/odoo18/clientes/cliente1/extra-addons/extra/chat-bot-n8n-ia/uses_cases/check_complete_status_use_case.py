# -*- coding: utf-8 -*-

import logging
import json
from odoo import models, api
from odoo.exceptions import ValidationError
import os
from pathlib import Path
import time

_logger = logging.getLogger(__name__)

class CheckCompleteStatusUseCase(models.TransientModel):
    _name = 'check_complete_status.use.case'
    _description = 'Check complete Use Case'

    @api.model
    def execute(self, options):
        try:
            openai_client = options.get('openai_client')
            thread_id = options.get('threadId')
            run_id = options.get('runId')
            
            max_time = 60  # segundos
            start_time = time.time()

            while True:
                run_status = openai_client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run_id
                )
                
                if run_status.status == 'completed':
                    return run_status

                # Verificar si ha pasado el tiempo máximo
                if time.time() - start_time > max_time:
                    return {"error": "Tiempo de espera agotado para la ejecución"}

                time.sleep(1)

            
        except Exception as e:
            _logger.error(f"Error al procesar la solicitud: {str(e)}")
            return {"error": f"Error en el procesamiento: {str(e)}"}