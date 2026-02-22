class FakeNotifier:
    """テスト用: 送信メッセージを記録するアダプタ."""

    def __init__(self) -> None:
        self._messages: list[str] = []

    @property
    def messages(self) -> frozenset[str]:
        """記録済みメッセージを不変セットで返す."""
        return frozenset(self._messages)

    def send(self, message: str) -> None:
        """メッセージをリストに記録する."""
        self._messages.append(message)
