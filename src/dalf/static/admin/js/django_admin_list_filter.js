'use strict';
{
    const $ = django.jQuery;

    $.fn.djangoAdminListFilterSelect2 = function() {
        $.each(this, function(i, element) {
            const ajaxURL = $(element).data("ajax--url");
            const appLabel = element.dataset.appLabel;
            const modelName = element.dataset.modelName;
            const fieldName = element.dataset.fieldName;
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
               var queryParam = fieldName + "__id__exact";

               navURL.searchParams.set(queryParam, decodeURIComponent(data.id));
               window.location.href = navURL.href;
            }).on("select2:unselect", function(e){
                var navURL = new URL(window.location.href);
                var queryParam = fieldName + "__id__exact";
                navURL.searchParams.delete(queryParam);
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
    
    function getQueryParams(e, isChoicesFilter) {
        var fieldName = e.target.name;
        var fieldQueryParam = isChoicesFilter ? `${fieldName}__exact` : `${fieldName}__id__exact`;
        var data = e.params.data;
        var selected = data.id.replace(/\?/, "");
        var queryParams = selected.split("&");
        if (queryParams.length === 1 && queryParams[0] === "") {
            queryParams = []
        }
        return [fieldQueryParam, queryParams];
    }
    
    $(document).ready(function() {
        $('.django-admin-list-filter').select2({
            allowClear: true,
            placeholder: gettext("Filter")
        }).on("select2:select", function(e){
            var navURL = new URL(window.location.href);
            let [fieldQueryParam, queryParams] = getQueryParams(e, $(this).data("isChoicesFilter"));
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
            let [fieldQueryParam, queryParams] = getQueryParams(e, $(this).data("isChoicesFilter"));

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
