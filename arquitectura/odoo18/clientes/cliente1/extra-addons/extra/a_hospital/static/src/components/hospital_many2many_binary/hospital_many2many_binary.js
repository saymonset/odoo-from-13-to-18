/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { UploadProgress } from "../upload_progress/upload_progress";

  export class Hospital_many2many_binary extends Component {
    static template = "a_hospital.Hospital_many2many_binary";
    static components = { UploadProgress };
    static props = {...standardFieldProps };
    setup() {
        super.setup(...arguments);
        this.notification = useService("notification");
        this.dialog = useService("dialog");
        this.uploadProgress = null;
    }

    _onUpload(ev) {
        const files = ev.target.files;
        const self = this;

        // Show the progress indicator in a dialog
        const progressState = useState({ percent: 0, title: _t("Uploading Files") });
        const closeProgress = this.dialog.add(UploadProgress, {
            title: _t("Uploading"),
            message: _t("Please wait while your files are being uploaded..."),
            onClose: () => {
                // Handle cancellation or user-triggered close
                closeProgress();
            }
        });
        // Create FormData for the upload
        const formData = new FormData();
        for (const file of files) {
            formData.append('ufile', file);
        }

        // Configure XMLHttpRequest to monitor progress (required for progress events)
        const xhr = new XMLHttpRequest();

        // Progress event
        xhr.upload.addEventListener('progress', function (e) {
            if (e.lengthComputable) {
                const percentComplete = (e.loaded / e.total) * 100;
                progressState.percent = Math.round(percentComplete);
            }
        }, false);
        // Completion event
        xhr.addEventListener('load', function () {
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
                    self.props.update(response);
                }
            } else {
                self.notification.add(_t("An error occurred during upload."), {
                    title: _t("Error"),
                    type: "danger",
                    sticky: true
                });
            }
        }, false);
         // Error event
        xhr.addEventListener('error', function () {
            closeProgress();
            self.notification.add(_t("An error occurred during upload."), {
                title: _t("Error"),
                type: "danger",
                sticky: true
            });
        }, false);

        // Send the request
        xhr.open('POST', '/web/binary/upload_attachment', true);
        xhr.setRequestHeader('X-Odoo-Session-Id', odoo.session_id);
        xhr.send(formData);

        // Clear the file input
        ev.target.value = '';
    }
     
  }

  registry.category("actions").add("hospital_many2many_binary", Hospital_many2many_binary);