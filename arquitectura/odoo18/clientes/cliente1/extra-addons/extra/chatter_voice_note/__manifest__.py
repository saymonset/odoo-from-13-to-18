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
            
            "https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js",
            "https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.5.25/jspdf.plugin.autotable.min.js",
            
           # 3. Componente del reporte médico (NUEVO)
            "chatter_voice_note/static/src/components/audio_to_text/medical_report.js",
            
            # 4. Componente principal
            "chatter_voice_note/static/src/components/audio_to_text/voice_recorder.js",
            
            # 5. Templates (cargar después de los componentes)
            "chatter_voice_note/static/src/components/audio_to_text/voice_recorder.xml",
            
            # 6. Acción cliente
            "chatter_voice_note/static/src/components/audio_to_text/audio_to_text.js",
            "chatter_voice_note/static/src/components/audio_to_text/audio_to_text.xml",
            
            # 7. CSS del reporte médico (NUEVO)
            "chatter_voice_note/static/src/components/audio_to_text/medical_report.css",
        
        ],
    },
    "installable": True,
}