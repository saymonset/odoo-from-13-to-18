{
    "name": "Chatter Voice Note",
    "version": "18.0.1.0.0",
    "category": "Tools",
    "depends": ["web", "base", "bus", "mail"],  # ✅ Agregar "mail" si es necesario
    "data": [
        "views/menu.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "chatter_voice_note/static/src/components/audio_to_text/bus_service.js",
            "chatter_voice_note/static/src/components/audio_to_text/voice_recorder.js",
            "chatter_voice_note/static/src/components/audio_to_text/audio_to_text.js",
            "chatter_voice_note/static/src/components/audio_to_text/voice_recorder.xml",
            "chatter_voice_note/static/src/components/audio_to_text/audio_to_text.xml",
        ],
    },
    "installable": True,
}