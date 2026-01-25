import json

from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import get_select2_language
from django.urls import reverse

__all__ = [
    'DALFChoicesField',
    'DALFModelAdmin',
    'DALFRelatedField',
    'DALFRelatedFieldAjax',
    'DALFRelatedFieldAjaxMulti',
    'DALFRelatedOnlyField',
]


class DALFModelAdmin(admin.ModelAdmin):
    @property
    def media(self):
        i18n_name = get_select2_language()
        i18n_file = (f'admin/js/vendor/select2/i18n/{i18n_name}.js',) if i18n_name else ()
        return super().media + forms.Media(
            js=(
                'admin/js/vendor/jquery/jquery.min.js',
                'admin/js/vendor/select2/select2.full.min.js',
                *i18n_file,
                'admin/js/jquery.init.js',
                'admin/js/django_admin_list_filter.js',
            ),
            css={
                'screen': (
                    'admin/css/vendor/select2/select2.min.css',
                    'admin/css/autocomplete.css',
                    'admin/css/django_admin_list_filter.css',
                ),
            },
        )


class DALFMixin:
    template = 'admin/filter/django_admin_list_filter.html'

    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)
        self.custom_template_params = {
            'app_label': model._meta.app_label,  # noqa: SLF001
            'model_name': model._meta.model_name,  # noqa: SLF001
            'field_name': field_path,
            'lookup_kwarg': self.lookup_kwarg,
        }

    def choices(self, changelist):
        yield from super().choices(changelist)
        yield {
            **self.custom_template_params,
        }


class DALFRelatedField(DALFMixin, admin.RelatedFieldListFilter):
    pass


class DALFRelatedOnlyField(DALFMixin, admin.RelatedOnlyFieldListFilter):
    pass


class DALFChoicesField(DALFMixin, admin.ChoicesFieldListFilter):
    pass


class DALFRelatedFieldAjax(admin.RelatedFieldListFilter):
    template = 'admin/filter/django_admin_list_filter_ajax.html'

    def __init__(self, field, request, params, model, model_admin, field_path):
        originial_params = dict(params)
        super().__init__(field, request, params, model, model_admin, field_path)

        source_model = field.model
        field_name = field_path.split('__')[-1]

        self.custom_template_params = {
            'app_label': source_model._meta.app_label,  # noqa: SLF001
            'model_name': source_model._meta.model_name,  # noqa: SLF001
            'field_name': field_name,
            'ajax_url': reverse('admin:autocomplete'),
            'lookup_kwarg': self.lookup_kwarg,
        }
        selected_value = originial_params.get(self.lookup_kwarg, [])
        self.selected_value = selected_value[0] if selected_value else None

        self.selected_text = None
        if self.selected_value:
            try:
                related_model = field.remote_field.model
                obj = related_model.objects.get(pk=self.selected_value)
                self.selected_text = str(obj)
            except (related_model.DoesNotExist, ValueError):
                self.selected_text = str(self.selected_value)

    def field_choices(self, _field, _request, _model_admin):
        return []

    def has_output(self):
        return True

    def choices(self, changelist):
        yield from super().choices(changelist)
        yield {
            **self.custom_template_params,
            'selected_value': self.selected_value,
            'selected_text': self.selected_text,
        }


class DALFRelatedFieldAjaxMulti(admin.FieldListFilter):
    template = 'admin/filter/django_admin_list_filter_ajax_multi.html'
    list_separator = ','

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.field = field
        self.field_path = field_path
        self.title = getattr(field, 'verbose_name', field_path)
        self.lookup_kwarg = f'{field_path}__in'

        source_model = field.model
        field_name = field_path.split('__')[-1]

        self.custom_template_params = {
            'app_label': source_model._meta.app_label,  # noqa: SLF001
            'model_name': source_model._meta.model_name,  # noqa: SLF001
            'field_name': field_name,
            'ajax_url': reverse('admin:autocomplete'),
            'lookup_kwarg': self.lookup_kwarg,
        }

        selected_param = params.get(self.lookup_kwarg, [''])[0]
        self.selected_values = [v for v in selected_param.split(self.list_separator) if v]

        self.selected_items = []
        if self.selected_values:
            related_model = field.remote_field.model
            for val in self.selected_values:
                try:
                    obj = related_model.objects.get(pk=val)
                    self.selected_items.append({'id': val, 'text': str(obj)})
                except (related_model.DoesNotExist, ValueError):
                    self.selected_items.append({'id': val, 'text': val})

        super().__init__(field, request, params, model, model_admin, field_path)

    def expected_parameters(self):
        return [self.lookup_kwarg]

    def has_output(self):
        return True

    def queryset(self, _request, queryset):
        if self.selected_values:
            return queryset.filter(**{self.lookup_kwarg: self.selected_values})
        return queryset

    def choices(self, changelist):
        yield {
            'selected': not self.selected_values,
            'query_string': changelist.get_query_string(remove=[self.lookup_kwarg]),
            'display': 'All',
        }
        yield {
            **self.custom_template_params,
            'selected_items_json': json.dumps(self.selected_items),
        }
