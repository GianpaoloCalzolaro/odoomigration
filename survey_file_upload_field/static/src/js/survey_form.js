import SurveyFormWidget from '@survey/js/survey_form';
import { getDataURLFromFile } from "@web/core/utils/urls";
import { _t } from "@web/core/l10n/translation";

SurveyFormWidget.include({

    events: Object.assign({}, SurveyFormWidget.prototype.events || {}, {
        'change .o_survey_question_upload_file': 'on_file_change',
    }),

    init() {
        this._super(...arguments);
        this.notification = this.bindService("notification");
    },

    start: function () {
        var self = this;
        return this._super.apply(this, arguments).then(function () {
            self.useFileAPI = !!window.FileReader;
            self.max_upload_size = 64 * 1024 * 1024; // 64Mo
            self.file_value = {};
            if (!self.useFileAPI) {
                self.fileupload_id = _.uniqueId('o_fileupload');
                $(window).on(self.fileupload_id, function () {
                    var args = [].slice.call(arguments).slice(1);
                    self.on_file_uploaded.apply(self, args);
                });
            }
        });
    },

    async on_file_change(e) {
        var self = this;
        var file_node = e.target;
        var files_list = [];
        if ((this.useFileAPI && file_node.files.length) || (!this.useFileAPI && $(file_node).val() !== '')) {
            if (this.useFileAPI) {
                var files = file_node.files;
                for (const file of files) {
                    if (file.size > this.max_upload_size) {
                        var message = _t("The selected file exceed the maximum file size of %s", this.max_upload_size);
                        this.notification.add(message, {
                            type: "danger",
                            sticky: true,
                            title: _t("File upload limit"),
                        });
                        file_node.value = null;
                        break;
                    }

                    await getDataURLFromFile(file).then(function (data) {
                        data = data.split(',')[1];
                        files_list.push({"file_name": file.name, "data": data});
                    });
                    self.file_value[$(file_node).data('questionId')] = files_list;
                    self.file_value[$(file_node).data('questionId')]['is_answer_update'] = true;
                }
            }
        }
    },

    _prepareSubmitValues: function (formData, params) {
        this._super.apply(this, arguments);
        var self = this;
        this.$('[data-question-type]').each(function () {
            switch ($(this).data('questionType')) {
                case 'upload_file':
                    if (self.file_value[$(this).data('questionId')]) {
                        params = self._prepareSubmitFiles(params, $(this), $(this).data('questionId'));
                        self.file_value[$(this).data('questionId')]['is_answer_update'] = false;
                    }
                    break;
            }
        });
    },

    _prepareSubmitFiles: function (params, $parent, questionId) {
        if (this.file_value[questionId]) {
            params[questionId] = {'values': this.file_value[questionId], 'is_answer_update': this.file_value[questionId]['is_answer_update']};
        }
        return params;
    },
});
