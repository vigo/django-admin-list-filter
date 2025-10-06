import os

import django
import pytest
from pytest_factoryboy import register

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testproject.settings')
django.setup()

from .factories import OrderFactory, PostFactory, TagFactory

register(TagFactory)
register(PostFactory)


@pytest.fixture
def posts():
    return PostFactory.create_batch(10)

@pytest.fixture
def unused_tag():
    return TagFactory(name='Unused')


@pytest.fixture
def orders():
    return OrderFactory.create_batch(3)
