# Naming Conventions

## General Rules

| Target | Convention | Example |
|---|---|---|
| Files / folders | snake_case | `content_types/content_type_a.py` |
| Classes | CamelCase | `FooClass` |
| Functions / methods | snake_case | `do_something` |
| Constants | UPPER_CASE | `CONSTANT_NAME` |
| Private members | Leading `_` | `_do_something` |
| Builtin conflicts | Trailing `_` | `property_` |
| Tests (happy path) | `test_*_happy_path` | `test_create_happy_path_with_valid_data` |
| Tests (error) | `test_*_error` | `test_create_error_with_missing_field` |
| Mocks | `mock_*` | `mock_doing` |

- Use descriptive names; avoid abbreviations (`cate` → `category`)

## Semantic Naming

| Type | Rule | Bad | Good |
|---|---|---|---|
| Boolean | `is_*` / `has_*` prefix | `enabled` | `is_enabled` |
| Collection | Plural form | `account_list` | `accounts` |
| Any | No type encoding in name | `name_str` | `name` |
