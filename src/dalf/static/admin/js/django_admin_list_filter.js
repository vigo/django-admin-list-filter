'use strict';
{
    const $ = django.jQuery;

    $.fn.djangoAdminListFilterSelect2 = function() {
        $.each(this, function(i, element) {
            const ajaxURL = $(element).data("ajax--url");
            const appLabel = element.dataset.appLabel;
            const modelName = element.dataset.modelName;
            const fieldName = element.dataset.fieldName;
            const lookupKwarg = element.dataset.lookupKwarg;
            const selectedValue = $(element).prev('.djal-selected-value').val();

            $(element).select2({
                ajax: {
                    data: (params) => {
                        return {
                            term: params.term,
                            page: params.page,
                            app_label: appLabel,
                            model_name: modelName,
                            field_name: fieldName
                        };
                    }
                }
            }).on('select2:select', function(e){
               var data = e.params.data;
               var navURL = new URL(window.location.href);

               navURL.searchParams.set(lookupKwarg, decodeURIComponent(data.id));
               window.location.href = navURL.href;
            }).on("select2:unselect", function(e){
                var navURL = new URL(window.location.href);
                navURL.searchParams.delete(lookupKwarg);
                window.location.href = navURL.href;
            });

            if (selectedValue){
                $.ajax({
                    url: ajaxURL,
                    dataType: "json",
                    data: {
                        term: "",
                        app_label: appLabel,
                        model_name: modelName,
                        field_name: fieldName
                    },
                    success: function(data){
                        if (data.results.length > 0) {
                            const selectedItem = data.results.find(item => item.id === selectedValue);
                            if (selectedItem) {
                                const selectedOption = new Option(selectedItem.text, selectedItem.id, true, true);
                                $(element).append(selectedOption).trigger("change");
                            }
                        };
                    }
                });
            }

        });
        return this;
    };

    function getQueryParams(e) {
        var fieldQueryParam = $(e.target).data('lookupKwarg');
        var data = e.params.data;
        var selected = data.id.replace(/\?/, "");
        var queryParams = selected.split("&");
        if (queryParams.length === 1 && queryParams[0] === "") {
            queryParams = []
        }
        return [fieldQueryParam, queryParams];
    }

    function getTextSafe(text) {
        /**
         * Safely retrieves the translated text using gettext if available.
         * Django doesn't always load the admin:jsi18n URL, for instance, when
         * has_delete_permission is set to false. In these cases, the gettext
         * function may be unavailable.
         * Reference: https://github.com/django/django/blob/main/django/contrib/admin/templates/admin/change_list.html#L10-L12
         *
        */
        if (typeof gettext !== 'undefined') {
            return gettext(text);
        } else {
            return text;
        }
    }

    $(document).ready(function() {
        $('.django-admin-list-filter').select2({
            allowClear: true,
            placeholder: getTextSafe("Filter")
        }).on("select2:select", function(e){
            var navURL = new URL(window.location.href);
            let [fieldQueryParam, queryParams] = getQueryParams(e);
            var isAllorEmptyChoice = true;

            queryParams.forEach(function(item){
                var [field, value] = item.split("=");
                if (field == fieldQueryParam) {
                    isAllorEmptyChoice = false;
                    navURL.searchParams.set(field, decodeURIComponent(value));
                }
            });
            if (isAllorEmptyChoice) {
                navURL.searchParams.delete(fieldQueryParam);
            }
            window.location.href = navURL.href;

        }).on("select2:unselect", function(e){
            var navURL = new URL(window.location.href);
            let [fieldQueryParam, queryParams] = getQueryParams(e);

            queryParams.forEach(function(item){
                var [field, value] = item.split("=");
                if (field == fieldQueryParam) {
                    navURL.searchParams.delete(field);
                }
            });

            window.location.href = navURL.href;
        });

        $('.django-admin-list-filter-ajax').djangoAdminListFilterSelect2();
    });
}
