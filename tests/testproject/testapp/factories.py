import factory
from django.contrib.auth import get_user_model
from factory import fuzzy

from .models import (
    AudienceChoices,
    Category,
    CategoryRenamed,
    Item,
    Order,
    Post,
    Product,
    Supplier,
    Tag,
)

FAKE_USERNAMES = [
    'vigo',
    'turbo',
    'move',
]

FAKE_CATEGORIES = [
    'Python',
    'Ruby',
    'Go',
    'Bash',
    'AppleScript',
    'C',
    'Perl',
]

FAKE_TAGS = [
    'django',
    'django rest',
    'linux',
    'macos',
    'stdlib',
]

FAKE_SUPPLIERS = [
    'Northwind Traders',
    'Contoso',
    'Adventure Works',
    'Globex',
]


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()
        django_get_or_create = ('username',)

    username = fuzzy.FuzzyChoice(FAKE_USERNAMES)
    email = factory.Faker('email')
    password = factory.PostGenerationMethodCall('set_password', 'defaultpassword')


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category
        django_get_or_create = ('name',)

    name = factory.Iterator(FAKE_CATEGORIES)


class CategoryRenamedFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CategoryRenamed
        django_get_or_create = ('name',)

    name = factory.Iterator(FAKE_CATEGORIES)


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag
        django_get_or_create = ('name',)

    name = fuzzy.FuzzyChoice(FAKE_TAGS)


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post
        django_get_or_create = ('title',)

    author = factory.SubFactory(UserFactory)
    category = factory.SubFactory(CategoryFactory)
    category_renamed = factory.SubFactory(CategoryRenamedFactory)
    title = factory.Sequence(lambda n: f'Book about {FAKE_CATEGORIES[n % len(FAKE_CATEGORIES)]} - {n}')
    audience = fuzzy.FuzzyChoice(AudienceChoices.choices, getter=lambda c: c[0])

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):  # noqa: ARG002
        if not create:
            return

        if extracted:
            self.tags.add(*extracted)
        else:
            tags = TagFactory.create_batch(len(FAKE_TAGS))
            self.tags.add(*tags)


class SupplierFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Supplier
        django_get_or_create = ('name',)

    name = factory.Iterator(FAKE_SUPPLIERS)


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Sequence(lambda n: f'Product {n}')
    supplier = factory.SubFactory(SupplierFactory)


class ItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Item

    name = factory.Sequence(lambda n: f'Item {n}')
    product = factory.SubFactory(ProductFactory)


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    reference = factory.Sequence(lambda n: f'Order-{n}')
    item = factory.SubFactory(ItemFactory)
