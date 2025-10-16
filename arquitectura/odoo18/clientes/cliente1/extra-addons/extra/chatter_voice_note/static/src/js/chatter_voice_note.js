odoo.define('chatter_voice_note.recorder', function (require) {
    "use strict";

    const rpc = require('web.rpc');

    function base64FromBlob(blob, cb) {
        const reader = new FileReader();
        reader.onload = function() { cb(reader.result.split(',')[1]); };
        reader.readAsDataURL(blob);
    }

    document.addEventListener('DOMContentLoaded', function () {
        const observer = new MutationObserver((mutations) => {
            for (const m of mutations) {
                for (const n of m.addedNodes) {
                    if (!(n instanceof HTMLElement)) continue;
                    const composers = n.querySelectorAll && n.querySelectorAll('.o_composer_text_input, .o_mail_thread .o_composer');
                    const nodes = composers && composers.length ? composers : document.querySelectorAll('.o_composer_text_input, .o_mail_thread .o_composer');
                    nodes.forEach(addMicIfMissing);
                }
            }
        });
        observer.observe(document.body, {childList: true, subtree: true});
        document.querySelectorAll('.o_composer_text_input, .o_mail_thread .o_composer').forEach(addMicIfMissing);
    });

    function addMicIfMissing(container) {
        if (!container || container._hasVoiceButton) return;
        container._hasVoiceButton = true;

        let actions = container.querySelector('.o_chatter_buttons, .o_composer_buttons, .o_mail_composer_buttons');
        if (!actions) {
            actions = document.createElement('div');
            actions.className = 'o_chatter_buttons';
            container.appendChild(actions);
        }

        const btn = document.createElement('button');
        btn.type = 'button';
        btn.title = 'Record voice note';
        btn.className = 'btn btn-sm btn-default o_voice_note_btn';
        btn.innerHTML = '<i class="fa fa-microphone"></i>';
        actions.appendChild(btn);

        let mediaRecorder = null;
        let chunks = [];

        btn.addEventListener('click', async function(ev) {
            ev.preventDefault();
            if (!mediaRecorder || mediaRecorder.state === 'inactive') {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream);
                    chunks = [];
                    mediaRecorder.ondataavailable = function(e) { if (e.data.size) chunks.push(e.data); };
                    mediaRecorder.onstop = async function() {
                        const blob = new Blob(chunks, { type: 'audio/webm' });
                        base64FromBlob(blob, async function(b64) {
                            const filename = 'voice_note_' + (new Date()).toISOString().replace(/[:.]/g,'_') + '.webm';
                            const vals = {
                                name: filename,
                                datas: b64,
                                res_model: false,
                                type: 'binary',
                                mimetype: 'audio/webm',
                            };
                            try {
                                const attach_id = await rpc.query({
                                    model: 'ir.attachment',
                                    method: 'create',
                                    args: [vals],
                                });

                                const composer = container.closest('[data-thread-id], [data-model], [data-res-id]') || container;
                                const model = composer.getAttribute ? composer.getAttribute('data-model') : null;
                                const res_id = composer.getAttribute ? composer.getAttribute('data-res-id') : null;

                                if (model && res_id) {
                                    await rpc.query({
                                        model: model,
                                        method: 'message_post',
                                        args: [parseInt(res_id)],
                                        kwargs: {
                                            body: '<p>Voice note</p>',
                                            attachment_ids: [attach_id],
                                        },
                                    });
                                } else {
                                    await rpc.query({
                                        model: 'mail.message',
                                        method: 'create',
                                        args: [{
                                            subject: 'Voice note',
                                            body: '<p>Voice note</p>',
                                            attachment_ids: [[6, 0, [attach_id]]],
                                        }],
                                    });
                                }
                                btn.classList.remove('btn-warning');
                                btn.classList.add('btn-success');
                                setTimeout(() => btn.classList.remove('btn-success'), 1200);
                            } catch (err) {
                                console.error('Attach/upload error', err);
                                alert('Error al subir la grabación: ' + (err.message || err));
                            }
                        });
                    };
                    mediaRecorder.start();
                    btn.classList.add('btn-warning');
                    btn.innerHTML = '<i class="fa fa-stop"></i>';
                } catch (err) {
                    console.error('No mic or permission denied', err);
                    alert('No se pudo acceder al micrófono. Usa HTTPS y permite el acceso al micrófono.');
                }
            } else if (mediaRecorder.state === 'recording') {
                mediaRecorder.stop();
                btn.innerHTML = '<i class="fa fa-microphone"></i>';
            }
        });
    }

});