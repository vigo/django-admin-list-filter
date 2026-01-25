'use strict';
{
    const $ = django.jQuery;

    $.fn.djangoAdminListFilterSelect2 = function() {
        $.each(this, function(i, element) {
            const appLabel = element.dataset.appLabel;
            const modelName = element.dataset.modelName;
            const fieldName = element.dataset.fieldName;
            const lookupKwarg = element.dataset.lookupKwarg;
            const selectedValue = $(element).prevAll('.djal-selected-value').first().val();
            const selectedText = $(element).prevAll('.djal-selected-text').first().val();

            $(element).select2({
                width: '100%',
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

            if (selectedValue && selectedText) {
                const selectedOption = new Option(selectedText, selectedValue, true, true);
                $(element).append(selectedOption).trigger("change");
            }

        });
        return this;
    };

    $.fn.djangoAdminListFilterSelect2Multi = function() {
        $.each(this, function(i, element) {
            const appLabel = element.dataset.appLabel;
            const modelName = element.dataset.modelName;
            const fieldName = element.dataset.fieldName;
            const lookupKwarg = element.dataset.lookupKwarg;

            const selectedItemsJson = $(element).prevAll('.djal-selected-items').first().val();
            const selectedItems = selectedItemsJson ? JSON.parse(selectedItemsJson) : [];

            $(element).select2({
                multiple: true,
                allowClear: true,
                width: '100%',
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
            }).on('change', function() {
                var selected = $(this).val() || [];
                var navURL = new URL(window.location.href);

                if (selected.length > 0) {
                    navURL.searchParams.set(lookupKwarg, selected.join(','));
                } else {
                    navURL.searchParams.delete(lookupKwarg);
                }
                window.location.href = navURL.href;
            });

            selectedItems.forEach(function(item) {
                var option = new Option(item.text, item.id, true, true);
                $(element).append(option);
            });
            if (selectedItems.length > 0) {
                $(element).trigger('change.select2');
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
        $('.django-admin-list-filter-ajax-multi').djangoAdminListFilterSelect2Multi();
    });
}
