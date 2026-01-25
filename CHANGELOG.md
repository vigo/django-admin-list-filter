# Change Log

**2026-01-25**

- Add `DALFRelatedFieldAjaxMulti` for multi-select filtering with AJAX support
- Multi-select uses comma-separated values with `__in` lookup (e.g., `?tags__in=uuid1,uuid2`)
- Selected items display as pill-shaped tags with remove buttons
- Fix clear button (×) incorrectly showing on non-AJAX filters when "All" was selected

---

**2026-01-24**

- Fix `DALFRelatedFieldAjax` filter repopulation bug - selected values beyond first 20 results now display correctly on page reload
- Add Python 3.14 to CI workflow matrix
- Upgrade ruff 0.13.3 → 0.14.14

---

**2024-09-06**

- Fix dark-mode text color.

---

**2024-08-25**

- Fix extend media in DALFModelAdmin without overriding default assets - [Bahattin][bahattincinic]

---

**2024-08-16**

- Add `gettextSafe` function to handle missing gettext in Django - [Bahattin][bahattincinic]

---

**2024-07-14**

- Fix choice.display last element issue

---

**2024-07-03**

- Now package is working fine :) Thanks to [Bahattin][bahattincinic]!

---

**2024-06-01**

- Update missing information in the README
- Improve github action triggers

---

**2024-05-23**

- Add tests
- Add GitHub actions (test, ruff linter)
- Add pre-commit hooks

---

**2024-05-20**

- Initial release.

---
