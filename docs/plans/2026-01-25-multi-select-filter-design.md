# Multi-Select Filter Design (Issue #15)

## Overview

Add multi-select capability to AJAX filters via new `DALFRelatedFieldAjaxMulti` class.

## Decisions

- **New class**: `DALFRelatedFieldAjaxMulti` (separate from existing)
- **URL format**: Comma-separated with `__in` lookup (`?category__id__in=5,8,12`)
- **Scope**: AJAX version only (non-AJAX deferred)
- **UI**: Select2 tags style

## Implementation

### Python (admin.py)

```python
class DALFRelatedFieldAjaxMulti(admin.FieldListFilter):
    template = 'admin/filter/django_admin_list_filter_ajax_multi.html'
    list_separator = ','

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg = f'{field_path}__in'
        # Parse comma-separated values, fetch display text for each
```

### Template

- New file: `django_admin_list_filter_ajax_multi.html`
- `multiple="multiple"` attribute
- JSON-encoded selected items

### JavaScript

- New function: `djangoAdminListFilterSelect2Multi()`
- `multiple: true` in Select2 config
- Single `change` event handler
- URL updated with `selected.join(',')`

## Test Cases

1. Multi-select filtering works
2. Page reload preserves selections
3. Deleted values handled gracefully
