# ruff: noqa: S101
import re
from html.parser import HTMLParser
from http import HTTPStatus

import pytest
from django.urls import reverse

from dalf.admin import DALFChoicesField, DALFRelatedField, DALFRelatedFieldAjax, DALFRelatedOnlyField

from .models import Post, Tag

csrf_token_pattern = re.compile(r'name="csrfmiddlewaretoken" value="([^"]+)"')


class MatchingTagValidator(HTMLParser):
    """Assert that a tag matching the given spec is found in the document.

    Instances of this class are not reusable. Create a new one for every ``check`` call.
    """

    def __init__(self, tag, matcher_attrs, expected_attrs, expected_content=None):
        super().__init__()
        self.matcher_attrs = matcher_attrs
        self.target_tag = tag
        self.expected_attrs = expected_attrs
        self.expected_content = expected_content
        self.seen_target_tag = False
        self.inside_target_tag = False

    def check(self, content):
        self.feed(content)
        assert self.seen_target_tag

    def handle_starttag(self, tag, attrs):
        if tag != self.target_tag:
            return
        attrs = dict(attrs)
        if self.matcher_attrs.items() <= attrs.items():
            self.inside_target_tag = True
            assert not self.seen_target_tag, 'Multiple matching tags found'
            self.seen_target_tag = True
            assert self.expected_attrs.items() <= attrs.items()

    def handle_endtag(self, tag):
        if tag == self.target_tag:
            # Yes, this will be incorrect with nested tags of same kind. We don't need
            # nested tags at all.
            self.inside_target_tag = False

    def handle_data(self, data):
        if self.inside_target_tag and self.expected_content is not None:
            assert data.strip() == self.expected_content



@pytest.mark.django_db
@pytest.mark.usefixtures('posts')
def test_post_admin_filters_basics(admin_client, unused_tag):
    posts_count = 10
    post_authors = dict(Post.objects.values_list('author__id', 'author__username'))
    post_audiences = {p.audience: p.get_audience_display() for p in Post.objects.all()}
    post_tags = dict(Tag.objects.filter(post__isnull=False).distinct().values_list('id', 'name'))

    assert post_authors
    assert post_audiences
    assert post_tags
    target_options = {'author': post_authors, 'audience': post_audiences, 'tags': post_tags}

    response = admin_client.get(reverse('admin:testapp_post_changelist'))
    assert response.status_code == HTTPStatus.OK
    assert len(response.context['results']) == posts_count
    assert response.context.get('cl', None)
    assert hasattr(response.context.get('cl', {}), 'filter_specs')

    content = response.content.decode()
    filter_specs = response.context['cl'].filter_specs

    assert len(filter_specs) > 0

    expected_lookup_kwargs = {
        'author': 'author__id__exact',
        'audience': 'audience__exact',
        'category': 'category__id__exact',
        'category_renamed': 'category_renamed__renamed_id__exact',
        'tags': 'tags__id__exact',
    }

    for spec in filter_specs:
        if isinstance(spec, (DALFRelatedField, DALFChoicesField, DALFRelatedFieldAjax, DALFRelatedOnlyField)):
            filter_choices = list(spec.choices(response.context['cl']))
            filter_custom_options = filter_choices.pop()
            option_field_name = filter_custom_options['field_name']

            lookup_kwarg = filter_custom_options['lookup_kwarg']
            assert lookup_kwarg == expected_lookup_kwargs[option_field_name]

            if option_field_name in ['author', 'audience', 'tags']:
                validator = MatchingTagValidator(
                    'select',
                    {'name': option_field_name},
                    {
                        'class': 'django-admin-list-filter admin-autocomplete',
                        'data-theme': 'admin-autocomplete',
                        'name': option_field_name,
                        'data-lookup-kwarg': lookup_kwarg,
                    },
                )
                validator.check(content)

                for internal, human in target_options[option_field_name].items():
                    validator = MatchingTagValidator(
                        'option',
                        {'value': f'?{lookup_kwarg}={internal}'},
                        {},
                        human
                    )
                    validator.check(content)

            elif option_field_name in ['category', 'category_renamed']:
                validator = MatchingTagValidator(
                    'select',
                    {'data-field-name': option_field_name},
                    {
                        'class': 'django-admin-list-filter-ajax',
                        'data-theme': 'admin-autocomplete',
                        'data-allow-clear': 'true',
                        'data-lookup-kwarg': lookup_kwarg,
                        'data-app-label': 'testapp',
                        'data-model-name': 'post',
                        'data-field-name': option_field_name,
                    },
                )
                validator.check(content)

                url_params = '&'.join(
                    [f'{key}={value}' for key, value in filter_custom_options.items() if key != 'selected_value']
                )
                url_params += '&term=Py'
                ajax_resonse = admin_client.get(f'/admin/autocomplete/?{url_params}')

                assert ajax_resonse['Content-Type'] == 'application/json'
                json_response = ajax_resonse.json()
                assert json_response

                results = json_response.get('results')
                assert len(results) == 1
                # Even when not named `id`, autocomplete AJAX will helpfully call it so:
                assert 'id' in results[0]

                pagination = json_response.get('pagination', {}).get('more', None)
                assert pagination is False
            else:
                pytest.fail(f'Unexpected field: {option_field_name}')

    # Must not include tags that have no associated Posts.
    validator = MatchingTagValidator(
        'option',
        {'value': f'?tags__id__exact={unused_tag.pk}'},
        {}
    )
    validator.feed(content)
    assert not validator.seen_target_tag
