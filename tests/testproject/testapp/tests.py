# ruff: noqa: S101
import re
from html.parser import HTMLParser
from http import HTTPStatus

import pytest
from django.urls import reverse

from dalf.admin import DALFChoicesField, DALFRelatedField, DALFRelatedFieldAjax, DALFRelatedOnlyField

from .models import Post

csrf_token_pattern = re.compile(r'name="csrfmiddlewaretoken" value="([^"]+)"')


class MatchingTagValidator(HTMLParser):
    """Assert that a tag matching the given spec is found in the document.

    Instances of this class are not reusable. Create a new one for every ``check`` call.
    """

    def __init__(self, expected_attrs, matcher_attrs, tag):
        super().__init__()
        self.expected_attrs = expected_attrs
        self.matcher_attrs = matcher_attrs
        self.target_tag = tag
        self.seen_target_tag = False

    def check(self, content):
        self.feed(content)
        assert self.seen_target_tag

    def handle_starttag(self, tag, attrs):
        if tag != self.target_tag:
            return
        attrs = dict(attrs)
        if self.matcher_attrs.items() <= attrs.items():
            assert not self.seen_target_tag, 'Multiple matching tags found'
            self.seen_target_tag = True
            assert self.expected_attrs.items() <= attrs.items()


@pytest.mark.django_db
def test_post_admin_filters_basics(admin_client, posts):  # noqa: ARG001
    posts_count = 10
    post_authors = set(Post.objects.values_list('author__username', flat=True))
    post_audiences = set(Post.objects.values_list('audience', flat=True))

    assert post_authors
    assert post_audiences

    response = admin_client.get(reverse('admin:testapp_post_changelist'))
    assert response.status_code == HTTPStatus.OK
    assert len(response.context['results']) == posts_count
    assert response.context.get('cl', None)
    assert hasattr(response.context.get('cl', {}), 'filter_specs')

    content = response.content.decode()
    filter_specs = response.context['cl'].filter_specs

    assert len(filter_specs) > 0

    for spec in filter_specs:
        if isinstance(spec, (DALFRelatedField, DALFChoicesField, DALFRelatedFieldAjax, DALFRelatedOnlyField)):
            filter_choices = list(spec.choices(response.context['cl']))
            filter_custom_options = filter_choices.pop()
            option_field_name = filter_custom_options.get('field_name', None)

            if option_field_name in ['author', 'audience']:
                maybe_id_suffix = '__id' if option_field_name == 'author' else ''
                validator = MatchingTagValidator(
                    {
                        'class': 'django-admin-list-filter admin-autocomplete',
                        'name': option_field_name,
                        'data-lookup-kwarg': f'{option_field_name}{maybe_id_suffix}__exact',
                        'data-theme': 'admin-autocomplete',
                    },
                    {'name': option_field_name},
                    'select',
                )
                validator.check(content)

            if option_field_name == 'author':
                for author in post_authors:
                    assert f'{author}</option>' in content

            if option_field_name == 'audience':
                for audience in post_audiences:
                    assert f'<option value="?audience__exact={audience}">' in content

            if option_field_name == 'category':
                assert 'data-field-name="category"></select>' in content

                url_params = '&'.join(
                    [f'{key}={value}' for key, value in filter_custom_options.items() if key != 'selected_value']
                )
                url_params += '&term=Py'
                ajax_resonse = admin_client.get(f'/admin/autocomplete/?{url_params}')

                assert ajax_resonse['Content-Type'] == 'application/json'

                json_response = ajax_resonse.json()
                assert json_response

                results = json_response.get('results')
                pagination = json_response.get('pagination', {}).get('more', None)

                assert len(results) == 1
                assert pagination is not None
                assert pagination is False
