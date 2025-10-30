
{
    "name": "Chatter Voice Note",
    "version": "18.0.1.0.0",
    "category": "Tools",
    "depends": ["web","base"],
    "data": [
        "views/menu.xml",
    ],
    "assets": {
        "web.assets_backend": [
             "chatter_voice_note/static/src/components/audio_to_text/audio_to_text.js",
             "chatter_voice_note/static/src/js/chatter_voice_note.js",
             "chatter_voice_note/static/src/components/audio_to_text/audio_to_text.xml",          
             "chatter_voice_note/static/xml/templates.xml"           
        ],
    },
    "installable": True,
}
