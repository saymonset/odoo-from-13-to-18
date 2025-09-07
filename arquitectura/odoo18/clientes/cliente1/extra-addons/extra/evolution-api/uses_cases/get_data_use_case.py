# -*- coding: utf-8 -*-

import logging
import locale
import json
from odoo import models, api
from odoo.exceptions import ValidationError
import os
from pathlib import Path
import time
from ..dto.get_info_whatsapp_dto import InfoWhatsAppDto
from datetime import datetime
import requests
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import hashlib, hmac
import subprocess

_logger = logging.getLogger(__name__)
try:
    locale.setlocale(locale.LC_TIME, 'es_VE.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')


class GetDataUseCase(models.TransientModel):
    _name = 'get_data.use.case'
    _description = 'Get data Use Case'

    @api.model
    def execute(self, options) -> dict:
        try:
            data = options.get('data')
            remote_jid = data.get('data', {}).get('key', {}).get('remoteJid')
            apikey = data.get('apikey')
            instance = data.get('instance')
            sender = data.get('sender')
            message_type = data.get('data', {}).get('messageType')
            message = data.get('data', {}).get('message', {})
            conversation = message.get('conversation')
            base64_str = message.get('base64')
            audio_message = message.get("audioMessage", {})
            media_url = audio_message.get("url")
            mediaKey = audio_message.get("mediaKey")

            # 1. Descargar el archivo cifrado
            enc_file = requests.get(media_url).content
            media_key = base64.b64decode(mediaKey)

            # 2. Derivar claves con HKDF
            def hkdf(key, length, app_info):
                key_stream = b""
                key_block = b""
                block_index = 1
                while len(key_stream) < length:
                    key_block = hmac.new(key, key_block + app_info + bytes([block_index]), hashlib.sha256).digest()
                    key_stream += key_block
                    block_index += 1
                return key_stream[:length]

            derived_key = hkdf(media_key, 112, b"WhatsApp Audio Keys")
            iv = derived_key[0:16]
            cipher_key = derived_key[16:48]

            # 3. Descifrar con AES-256-CBC
            cipher = AES.new(cipher_key, AES.MODE_CBC, iv)
            enc_file_trimmed = enc_file[:-10]
            decrypted = cipher.decrypt(enc_file_trimmed)

            try:
                decrypted = unpad(decrypted, AES.block_size)
            except ValueError:
                _logger.warning("El padding no era válido, se deja el buffer tal cual")

            # 4. Buscar cabecera OGG y limpiar basura
            ogg_header = b"OggS"
            start = decrypted.find(ogg_header)
            if start == -1:
                _logger.error("No se encontró cabecera OggS en el audio descifrado")
            else:
                decrypted = decrypted[start:]
                last = decrypted.rfind(ogg_header)
                if last > start:
                    decrypted = decrypted[:last] + decrypted[last:]

            # 5. Guardar primero como OGG
            folder_path = Path(__file__).parent.resolve() / '../generated/audios/'
            folder_path = folder_path.resolve()
            os.makedirs(folder_path, exist_ok=True)

            timestamp = int(time.time() * 1000)
            ogg_path = folder_path / f"{timestamp}.ogg"
            mp3_path = folder_path / f"{timestamp}.mp3"

            with open(ogg_path, 'wb') as f:
                f.write(decrypted)

            # 6. Convertir a MP3 con ffmpeg (más robusto que pydub)
            try:
                subprocess.run(
                    ["ffmpeg", "-y", "-i", str(ogg_path), str(mp3_path)],
                    check=True, capture_output=True
                )
                final_file = mp3_path
            except subprocess.CalledProcessError as conv_err:
                _logger.error(f"ffmpeg no pudo convertir OGG a MP3: {conv_err.stderr.decode(errors='ignore')}")
                final_file = ogg_path

            # ---- Manejo de datos ----
            client_phone = None
            if remote_jid and '@' in remote_jid:
                client_phone = remote_jid.split('@')[0]
            else:
                raise ValidationError("No se pudo extraer el client_phone de remoteJid")

            host_phone = None
            if sender and '@' in sender:
                host_phone = sender.split('@')[0]
            else:
                raise ValidationError("No se pudo extraer el host_phone de sender")

            if not all([host_phone, client_phone, message_type, instance, apikey]):
                missing_fields = [field for field, value in [
                    ("host_phone", host_phone),
                    ("client_phone", client_phone),
                    ("message_type", message_type),
                    ("instance", instance),
                    ("apikey", apikey)
                ] if not value]
                raise ValidationError(f"Faltan campos requeridos: {', '.join(missing_fields)}")

            infoWhatsAppDto = InfoWhatsAppDto(
                host_phone=host_phone,
                client_phone=client_phone,
                message_type=message_type,
                conversation=conversation,
                instance=instance,
                apikey=apikey,
                base64=base64_str,
                media_url=media_url,
                timestamp=datetime.now()
            )

            return {
                **infoWhatsAppDto.dict(),
                "saved_file": str(final_file)  # ruta final del archivo MP3/OGG
            }

        except Exception as e:
            _logger.error(f"Error al procesar la solicitud: {str(e)}")
            return {"error": f"Error en el procesamiento: {str(e)}"}
