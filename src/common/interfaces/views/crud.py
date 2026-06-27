"""CRUD の汎用ビュー基底 (DRF).

入力検証 (deserializer) → フック (具象が usecase を呼ぶ) →
出力整形 (serializer) → ステータス、という HTTP 配管を共通化する。
具象は serializer/deserializer クラスと 5 つのフックを実装する。

存在しない ID は ``EntityDoesNotExistError`` を送出し、共通例外
ハンドラが 404 に変換する (本基底では捕捉しない = 取りこぼし防止)。

NOTE: DRF が一覧アクションを ``list`` という名前で要求し、クラス内で組み込み
``list`` を隠蔽する。注釈に ``list[...]`` を書くと型チェッカが混乱するため、
フックの戻り値は ``Sequence`` で表現する。
"""

from collections.abc import Sequence
from typing import Any
from typing import ClassVar
from typing import cast

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.viewsets import ViewSet


class CrudViewSet(ViewSet):
    """create/get/list/update/delete の HTTP 配管を提供する基底."""

    output_serializer_class: ClassVar[type[BaseSerializer[Any]]]
    input_deserializer_class: ClassVar[type[BaseSerializer[Any]]]

    # --- 具象が実装するフック (usecase 呼び出し) ---

    def perform_create(self, data: dict[str, Any]) -> Any:
        """検証済みデータからエンティティを作成して返す."""
        raise NotImplementedError

    def perform_get(self, pk: str) -> Any:
        """ID でエンティティを取得して返す."""
        raise NotImplementedError

    def perform_list(
        self,
        *,
        page: int,
        page_size: int,
    ) -> tuple[Sequence[Any], int]:
        """一覧と総件数を返す."""
        raise NotImplementedError

    def perform_update(
        self,
        pk: str,
        data: dict[str, Any],
    ) -> Any:
        """検証済みデータでエンティティを更新して返す."""
        raise NotImplementedError

    def perform_delete(self, pk: str) -> None:
        """ID でエンティティを削除する."""
        raise NotImplementedError

    # --- DRF アクション (配管) ---

    def list(self, request: Request) -> Response:
        """一覧を返す."""
        page, page_size = self._pagination_params(request)
        entities, total = self.perform_list(page=page, page_size=page_size)
        serializer = self.output_serializer_class(
            instance=entities,
            many=True,
        )
        return Response({"count": total, "results": serializer.data})

    def create(self, request: Request) -> Response:
        """新規作成して 201 を返す."""
        data = self._validate(request.data)
        entity = self.perform_create(data)
        serializer = self.output_serializer_class(instance=entity)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(
        self,
        _request: Request,
        pk: str,
    ) -> Response:
        """単一取得して返す."""
        entity = self.perform_get(pk)
        serializer = self.output_serializer_class(instance=entity)
        return Response(serializer.data)

    def update(
        self,
        request: Request,
        pk: str,
    ) -> Response:
        """全項目更新して返す."""
        data = self._validate(request.data)
        entity = self.perform_update(pk, data)
        serializer = self.output_serializer_class(instance=entity)
        return Response(serializer.data)

    def partial_update(
        self,
        request: Request,
        pk: str,
    ) -> Response:
        """部分更新して返す."""
        data = self._validate(request.data, partial=True)
        entity = self.perform_update(pk, data)
        serializer = self.output_serializer_class(instance=entity)
        return Response(serializer.data)

    def destroy(
        self,
        _request: Request,
        pk: str,
    ) -> Response:
        """削除して 204 を返す."""
        self.perform_delete(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def _pagination_params(request: Request) -> tuple[int, int]:
        """page/page_size を検証して返す (不正は 400)."""
        try:
            page = int(request.query_params.get("page", "1"))
            page_size = int(request.query_params.get("page_size", "10"))
        except ValueError as exc:
            msg = "page と page_size は整数で指定してください"
            raise ValidationError(msg) from exc
        if page < 1 or page_size < 1:
            msg = "page と page_size は 1 以上で指定してください"
            raise ValidationError(msg)
        return page, page_size

    def _validate(
        self,
        data: Any,
        *,
        partial: bool = False,
    ) -> dict[str, Any]:
        """入力を deserializer で検証し、検証済み dict を返す."""
        deserializer = self.input_deserializer_class(
            data=data,
            partial=partial,
        )
        deserializer.is_valid(raise_exception=True)
        return cast("dict[str, Any]", deserializer.validated_data)
