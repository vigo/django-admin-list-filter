import pytest
from pytest_factoryboy import register

from .factories import PostFactory, TagFactory

register(TagFactory)
register(PostFactory)


@pytest.fixture
def posts():
    return PostFactory.create_batch(10)

@pytest.fixture
def unused_tag():
    return TagFactory(name='Unused')
