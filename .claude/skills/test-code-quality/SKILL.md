---
name: test-code-quality
description: Test code quality reference for pytest. Use when writing, reviewing, or refactoring tests for best practices, naming, parametrize, hypothesis, fixtures, and test doubles.
---

# Test Code Quality Guide

## Arrange-Act-Assert (AAA)

Every test follows the AAA pattern with section markers.
When sections are trivially combined, use `# Arrange & Act`
or `# Act & Assert`.

```python
def test_happy_sends_message(self) -> None:
    """タイトルと著者名を含むメッセージが送信されること."""
    # Arrange
    fake = FakeNotifier()
    use_case = NotifyBookCreatedUseCaseImpl(
        notifier=fake,
        logger_factory=_real_factory,
    )
    event = BookCreated(
        title="吾輩は猫である",
        isbn="9784003101018",
        author_name="夏目漱石",
    )

    # Act
    result = use_case.execute(event=event)

    # Assert
    assert isinstance(result, NotificationSuccess)
    (msg,) = fake.messages
    assert "吾輩は猫である" in msg
```

| Pattern | When |
|---|---|
| `# Arrange` / `# Act` / `# Assert` | Default: three distinct phases |
| `# Arrange & Act` | Construction IS the action under test |
| `# Act & Assert` | `pytest.raises` wrapping a single call |

## Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Happy-path test | `test_happy_<behavior>` | `test_happy_creates_event` |
| Error test | `test_error_<behavior>` | `test_error_rejects_empty_string` |
| Test class | `Test<Subject>` | `TestBookCreated` |
| Valid group class | `Test<Subject>Valid` | `TestSafeTextValid` |
| Invalid group class | `Test<Subject>Invalid` | `TestSafeTextInvalid` |
| Docstring (happy) | Japanese `"""正常系: ...."""` | `"""正常系: 許可されるテキスト"""` |
| Docstring (error) | Japanese `"""異常系: ...."""` | `"""異常系: 拒否されるテキスト"""` |

## pytest.mark.parametrize

Always provide `ids` for readable test output. Use tuple
unpacking for multi-value parameters.

| Rule | Bad | Good |
|---|---|---|
| Missing ids | `@parametrize("x", [1, 2])` | `@parametrize("x", [1, 2], ids=["one", "two"])` |
| Multi-param | Separate decorators | Tuple `("field", "payload")` |
| ID naming | `ids=["1", "2"]` | `ids=["hiragana", "english"]` |

```python
# Single parameter
@pytest.mark.parametrize(
    "text",
    [
        "ひらがな",
        "Hello World",
        "Python入門",
    ],
    ids=[
        "hiragana",
        "english",
        "mixed_ja_en",
    ],
)
def test_happy_accepts_valid_text(self, text: str) -> None:
    ...

# Multiple parameters with tuple unpacking
@pytest.mark.parametrize(
    ("missing_field", "payload_without"),
    [
        (
            "title",
            {"isbn": "9784003101025", "published_date": "1906-04-01"},
        ),
        (
            "isbn",
            {"title": "テスト", "published_date": "1906-04-01"},
        ),
    ],
    ids=["title", "isbn"],
)
def test_error_rejects_missing_field(
    self,
    missing_field: str,
    payload_without: dict[str, str],
) -> None:
    ...
```

## Hypothesis / Property-Based Testing

Use `@given` to verify properties hold for arbitrary inputs.
Define reusable strategies as module-level constants.

| When to Use | Example |
|---|---|
| Value object accepts a range of inputs | `SafeText` with safe Unicode |
| Domain invariant must hold for all data | Event fields always in message |
| Boundary validation with character classes | Reject symbol categories |

| Rule | Bad | Good |
|---|---|---|
| Reuse | Duplicate `st.text(...)` per test | Module-level `_non_empty_text = st.text(...)` |
| Empty strings | Bare `st.text()` | `st.text(min_size=1).filter(lambda s: s.strip())` |
| Character sets | Random `st.text()` hoping for coverage | `st.characters(whitelist_categories=("L", "N"))` |

```python
# Module-level reusable strategy
_non_empty_text = st.text(min_size=1).filter(
    lambda s: s.strip()
)

# Happy: property holds for any valid input
@given(
    title=_non_empty_text,
    isbn=_non_empty_text,
    author_name=_non_empty_text,
)
def test_happy_message_contains_event_fields(
    self,
    title: str,
    isbn: str,
    author_name: str,
) -> None:
    """メッセージにイベントのフィールドが含まれること."""
    # Arrange
    fake = FakeNotifier()
    use_case = NotifyBookCreatedUseCaseImpl(
        notifier=fake, logger_factory=_real_factory,
    )
    event = BookCreated(
        title=title, isbn=isbn, author_name=author_name,
    )

    # Act
    result = use_case.execute(event=event)

    # Assert
    assert isinstance(result, NotificationSuccess)
    (msg,) = fake.messages
    assert title in msg

# Error: property holds for unsafe categories
@given(
    text=st.text(
        min_size=1,
        max_size=255,
        alphabet=st.characters(
            whitelist_categories=("So", "Sk"),
        ),
    )
)
def test_error_rejects_any_unsafe_text(self, text: str) -> None:
    """異常系: 記号カテゴリの任意テキストが拒否されること."""
    with pytest.raises(ValueError, match="使用できない文字"):
        SafeText(value=text)
```

## Fixtures

| Rule | Bad | Good | Why |
|---|---|---|---|
| Scope | `scope="session"` for mutable | Default (function) | Test isolation |
| Cleanup | Manual in test body | `Generator` + `yield` | Guaranteed teardown |
| Setup | Explicit in every test | `autouse=True` | Less boilerplate |
| Autouse name | Public name | Leading `_`: `_memory_storage` | Signal "not called directly" |
| Type hint | `-> Any` | `-> Generator[T]` | Explicit yield type |
| DB access | Implicit | `db: Any` param or `@pytest.mark.django_db` | Clear dependency |

```python
# autouse: leading underscore, no return value
@pytest.fixture(autouse=True)
def _memory_storage(settings: Any) -> None:
    """テスト用にインメモリストレージを使用する."""
    settings.STORAGES = {
        "default": {
            "BACKEND": (
                "django.core.files.storage.InMemoryStorage"
            ),
        },
    }

# Generator with yield + cleanup
@pytest.fixture
def fake_notifier() -> Generator[FakeNotifier]:
    """テスト用の FakeNotifier を DI に差し込む."""
    notifier = FakeNotifier()
    container.override(
        NotificationModule(notifier_override=notifier),
    )
    yield notifier
    container.reset()

# DB fixture: explicit db dependency
@pytest.fixture
def author(db: Any) -> Author:
    return Author.objects.create(
        name="夏目漱石", bio="日本の小説家",
    )
```

## Test Doubles

Prefer manual test doubles over `unittest.mock.patch`.
Use `mock.patch` only for I/O boundaries that cannot be
replaced via DI.

| Type | Naming | Location | Purpose |
|---|---|---|---|
| Stub | `_StubXxx` | Test module (private) | Return fixed values |
| Fake | `FakeXxx` | `infrastructure/adapters/` | Lightweight real impl |
| Failing | `_FailingXxx` | Test module (private) | Raise on call |
| Autospec | `mock_logger` | Test method body | Verify interaction |
| `mock.patch` | Last resort | Test method body | External I/O only |

### Prefer create_autospec When Mocking

Never use `MagicMock()` or `Mock()` directly.
`create_autospec` validates signatures, preventing drift
between implementation and mock.

| Rule | Bad | Good | Why |
|---|---|---|---|
| Mock creation | `MagicMock()` | `create_autospec(Cls, instance=True)` | Type and signature validation |
| `spec` vs `autospec` | `Mock(spec=Cls)` | `create_autospec(Cls)` | Validates nested attributes too |

```python
# Bad: MagicMock does not validate signatures
mock_logger = MagicMock()
mock_logger.waning("typo")  # silently passes

# Good: create_autospec raises on signature mismatch
mock_logger = create_autospec(
    logging.Logger, instance=True,
)
mock_logger.waning("typo")  # AttributeError
```

**Caveat: cases where `create_autospec` does not work**

| Case | Reason | Fallback |
|---|---|---|
| C extension types (`ssl.SSLSocket` etc.) | Cannot introspect | `Mock(spec=Cls)` |
| `__slots__` + dynamic attributes | Incomplete attribute enumeration | `Mock(spec=Cls)` |
| `@property` with side effects | Property executes during spec creation | `Mock(spec_set=Cls)` |
| Protocol without `__init__` | No signature information available | Manual Stub class |

When in doubt, try `create_autospec` first and fall back to
the alternatives above if it raises.

```python
# Stub: fixed return (private, in test file)
class _StubLoggerFactory:
    """テスト用: 固定の mock Logger を返すファクトリ."""

    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger

    def build(self, name: str) -> logging.Logger:
        return self._logger

# Fake: lightweight impl (public, in src/)
class FakeNotifier:
    """テスト用: 送信メッセージを記録するアダプタ."""

    def __init__(self) -> None:
        self._messages: list[str] = []

    def send(self, message: str) -> None:
        self._messages.append(message)

# Failing: raises on call (private, in test file)
class _FailingNotifier:
    """send 時に例外を投げるテスト用 Notifier."""

    def send(self, message: str) -> None:
        msg = "送信失敗"
        raise RuntimeError(msg)
```

## DI Container Testing

| Rule | Bad | Good |
|---|---|---|
| Override | `mock.patch` internal | `container.override(Module(...))` |
| Reset | Forget to reset | `container.reset()` after yield |
| Pattern | Override in each test | Fixture with `yield` + `reset()` |

```python
@pytest.fixture
def fake_notifier() -> Generator[FakeNotifier]:
    """テスト用の FakeNotifier を DI に差し込む."""
    notifier = FakeNotifier()
    container.override(
        NotificationModule(notifier_override=notifier),
    )
    yield notifier
    container.reset()
```
