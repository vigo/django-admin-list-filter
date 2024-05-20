![Version](https://img.shields.io/badge/version-0.0.0-orange.svg?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.11+-green.svg?style=for-the-badge)
![Django](https://img.shields.io/badge/django-5.0.2-green.svg?style=for-the-badge)
[![Ruff](https://img.shields.io/endpoint?style=for-the-badge&url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

# Django Admin List Filter

Dead simple autocompletion for Django admin `list_filter`. This was made using
the libraries shipped with Django (`select2`, `jquery`), Django’s built-in
list filters, and Django’s built-in `AutocompleteJsonView`.

This package is an **improved** version of the previously created 
[django-admin-autocomplete-list-filter][1] package. It supports Django **version 5** and 
above. Please note that the *django-admin-autocomplete-list-filter* package is 
now **deprecated**. Since I am no longer part of the organization where it was 
initially developed, I cannot archive it.

No extra package or install required!

Before **Django Admin List Filter**

![Before Django Admin List Filter](screens/before-dalf.gif)

After **Django Admin List Filter**

![After Django Admin List Filter](screens/after-dalf.gif?1)

---

## Installation

```bash
pip install django-admin-list-filter
```

Add `dalf` to your `INSTALLED_APPS` in your `settings.py`:

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "dalf", # <- add
]
```

---

## Usage

Use `DALFModelAdmin`, inherited from `admin.ModelAdmin` to inject media urls only.
You have some filters;

- `DALFRelatedField`: inherited from `admin.RelatedFieldListFilter`.
- `DALFRelatedFieldAjax`: inherited from `admin.RelatedFieldListFilter`
- `DALFRelatedOnlyField`: inherited from `admin.RelatedOnlyFieldListFilter`.
- `DALFChoicesField`: inherited from `admin.ChoicesFieldListFilter`.

Example `models.py`

```python
# models.py
import uuid

from django.conf import settings
from django.db import models


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Tag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(to='Category', on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=255)
    body = models.TextField()
    tags = models.ManyToManyField(to='Tag', blank=True)

    def __str__(self):
        return self.title
```

Example `admin.py`:

```python
# admin.py
from dalf.admin import DALFModelAdmin, DALFRelatedOnlyField, DALFRelatedFieldAjax
from django.contrib import admin


@admin.register(Post)
class PostAdmin(DALFModelAdmin):
    list_filter = (
        ('author', DALFRelatedOnlyField),    # if author has a post!
        ('category', DALFRelatedFieldAjax),  # enable ajax completion for category field (FK)
        ('tags', DALFRelatedFieldAjax),      # enable ajax completion for tags field (M2M)
    )
```

That’s all... There is also `DALFChoicesField`, you can test it out:

```python
# admin.py
from dalf.admin import DALFModelAdmin, DALFChoicesField, DALFRelatedOnlyField, DALFRelatedFieldAjax
from django.contrib import admin


@admin.register(Post)
class PostAdmin(DALFModelAdmin):
    list_filter = (
        ('author', DALFChoicesField),        # enable autocomplete w/o ajax (FK)
        ('category', DALFRelatedFieldAjax),  # enable ajax completion for category field (FK)
        ('tags', DALFRelatedOnlyField),      # enable ajax completion for tags field (M2M) if posts has any tag!
    )
```

### Extras

I mostly use `django-timezone-field`, here is an illustration of timezone
completion w/o **ajax**:

```bash
pip install django-timezone-field
```

Now add `timezone` field to `Post` model:

```python
# modify models.py, add new ones
from timezone_field import TimeZoneField                 # <- add this line

class Post(models.Model):
    # all the other fiels
    timezone = TimeZoneField(default=settings.TIME_ZONE) # <- add this line
    
    # rest of the code
```

Now, just add `timezone` as regular `list_filter`:

```python
# modify admin.py, add new ones

@admin.register(Post)
class PostAdmin(DALFModelAdmin):
    # previous codes
    list_filter = (
        # previous filters
        ('timezone', DALFChoicesField), # <- add this line
    )
```

That’s it!

---

## Contributor(s)

* [Uğur Özyılmazel](https://github.com/vigo) - Creator, maintainer

---

## Contribute

All PR’s are welcome!

1. `fork` (https://github.com/vigo/django-admin-list-filter/fork)
1. Create your `branch` (`git checkout -b my-feature`)
1. `commit` yours (`git commit -am 'add some functionality'`)
1. `push` your `branch` (`git push origin my-feature`)
1. Than create a new **Pull Request**!

I am not very proficient in JavaScript. Therefore, any support, suggestions,
and feedback are welcome to help improve the project. Feel free to open
pull requests!

---

## Development

Clone the repo somewhere, and install with:

```bash
pip install -e /path/to/django-admin-list-filter
```

And play with the filters :)

---

## Change Log

**2024-05-20**

- Initial release.

---

You can read the whole story [here][changelog].

---

## License

This project is licensed under MIT

---

This project is intended to be a safe, welcoming space for collaboration, and
contributors are expected to adhere to the [code of conduct][coc].

[1]: https://github.com/demiroren-teknoloji/django-admin-autocomplete-list-filter "Deprecated, old package"
[coc]: https://github.com/vigo/django-admin-list-filter/blob/main/CODE_OF_CONDUCT.md
[changelog]: https://github.com/vigo/django-admin-list-filter/blob/main/CHANGELOG.md
