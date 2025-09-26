/** @odoo-module **/
import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { UploadProgress } from "../upload_progress/upload_progress";

export class Hospital_many2many_binary extends Component {
    static template = "a_hospital.Hospital_many2many_binary";
    static props = { ...standardFieldProps };
    static components = { UploadProgress };

    setup() {
        super.setup(...arguments);
        this.notification = useService("notification");
        this.dialog = useService("dialog");
        this.progressState = useState({ percent: 0 });
    }

    _onUpload(ev) {
        const files = ev.target.files;
        if (!files.length) return;
        const self = this;

        const closeProgress = this.dialog.add(UploadProgress, {
            title: _t("Uploading Files"),
            message: _t("Please wait while your files are being uploaded..."),
            onClose: () => closeProgress(),
        });

        const formData = new FormData();
        for (const file of files) {
            formData.append('ufile', file);
        }

        const xhr = new XMLHttpRequest();

        xhr.upload.addEventListener("progress", function(e) {
            if (e.lengthComputable) {
                self.progressState.percent = Math.round((e.loaded / e.total) * 100);
            }
        });

        xhr.addEventListener("load", function() {
            closeProgress();
            if (xhr.status === 200) {
                const response = JSON.parse(xhr.responseText);
                if (response.error) {
                    self.notification.add(_t("Upload Error"), {
                        title: _t("Error"),
                        type: "danger",
                        sticky: true,
                        message: response.error
                    });
                } else {
                    // actualizar campo Many2many
                    const attachments = response.map(file => ({ id: file.id }));
                    self.props.update({ value: self.props.value.concat(attachments) });
                }
            } else {
                self.notification.add(_t("Upload failed"), { type: "danger" });
            }
        });

        xhr.open("POST", "/web/binary/upload_attachment", true);
        xhr.setRequestHeader("X-Odoo-Session-Id", odoo.session_id);
        xhr.send(formData);

        ev.target.value = "";
    }
}

// Registrar widget para Many2many
registry.category("fields").add("hospital_many2many_binary", Hospital_many2many_binary);
