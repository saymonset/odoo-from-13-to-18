{
    "name": "Chatter Voice Note",
    "version": "18.0.1.0.0",
    "category": "Tools",
    "depends": ["web", "base", "bus", "mail"],
    "data": [
        "views/menu.xml",
    ],
    "assets": {
        "web.assets_backend": [
            # 1. Constantes y utilidades
            "chatter_voice_note/static/src/components/audio_to_text/constants.js",
            
            # 2. Servicios y managers
            "chatter_voice_note/static/src/components/audio_to_text/contact_manager.js",
            "chatter_voice_note/static/src/components/audio_to_text/audio_recorder.js",
            "chatter_voice_note/static/src/components/audio_to_text/audio_note_manager.js",
            "chatter_voice_note/static/src/components/audio_to_text/n8n_service.js",
            
            # 3. Componente principal (debe cargarse ANTES de la acción)
            "chatter_voice_note/static/src/components/audio_to_text/voice_recorder.js",
            "chatter_voice_note/static/src/components/audio_to_text/voice_recorder.xml",
            
            # 4. Acción cliente (debe cargarse DESPUÉS del componente)
            "chatter_voice_note/static/src/components/audio_to_text/audio_to_text.js",
            "chatter_voice_note/static/src/components/audio_to_text/audio_to_text.xml",
        ],
    },
    "installable": True,
}