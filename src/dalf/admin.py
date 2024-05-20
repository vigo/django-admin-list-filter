# ruff: noqa: PLR0913,ARG002,SLF001
import json

from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import get_select2_language
from django.urls import reverse

__all__ = [
    'DALFModelAdmin',
    'DALFRelatedField',
    'DALFRelatedOnlyField',
    'DALFChoicesField',
    'DALFRelatedFieldAjax',
]


class DALFModelAdmin(admin.ModelAdmin):
    @property
    def media(self):
        i18n_name = get_select2_language()
        i18n_file = (f'admin/js/vendor/select2/i18n/{i18n_name}.js',) if i18n_name else ()
        return forms.Media(
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
                    'admin/css/django_admin_list_filter.css',
                ),
            },
        )


class DALFMixin:
    template = 'admin/filter/django_admin_list_filter.html'

    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)
        self.custom_template_params = {
            'app_label': model._meta.app_label,
            'model_name': model._meta.model_name,
            'field_name': field_path,
            'is_choices_filter': json.dumps(obj=False),
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
    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)
        self.custom_template_params.update({'is_choices_filter': json.dumps(obj=True)})


class DALFRelatedFieldAjax(admin.RelatedFieldListFilter):
    template = 'admin/filter/django_admin_list_filter_ajax.html'

    def __init__(self, field, request, params, model, model_admin, field_path):
        originial_params = dict(params)
        super().__init__(field, request, params, model, model_admin, field_path)

        self.custom_template_params = {
            'app_label': model._meta.app_label,
            'model_name': model._meta.model_name,
            'field_name': field_path,
            'ajax_url': reverse('admin:autocomplete'),
        }
        selected_value = originial_params.get(self.lookup_kwarg, [])
        self.selected_value = selected_value[0] if selected_value else None

    def field_choices(self, field, request, model_admin):
        return []

    def has_output(self):
        return True

    def choices(self, changelist):
        yield from super().choices(changelist)
        yield {
            **self.custom_template_params,
            'selected_value': self.selected_value,
        }
