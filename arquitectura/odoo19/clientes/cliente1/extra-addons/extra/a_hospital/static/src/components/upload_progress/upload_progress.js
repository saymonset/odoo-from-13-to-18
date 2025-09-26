/** @odoo-module **/
import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export class UploadProgress extends Component {
    static template = "a_hospital.Upload_progress";
    static props = {
        title: {
            type: String,
            optional: true,
            default: _t("Uploading")
        },
        message: {
            type: String,
            optional: true,
            default: _t("Please wait while your files are being uploaded...")
        },
        onClose: {
            type: Function,
            optional: true
        }
    };

    setup() {
        this.state = useState({ percent: 0 });
    }
    updateProgress(percent) {
        if (this.state) {
            this.state.percent = Math.round(percent);
        }
    }

    onClose() {
        if (this.props.onClose) {
            this.props.onClose();
        }
    }
}
