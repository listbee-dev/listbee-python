from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from pydantic import BaseModel

if TYPE_CHECKING:
    from listbee._base_client import AsyncClient, SyncClient

T = TypeVar("T", bound=BaseModel)


class SyncCursorPage(Generic[T]):
    """A paginated list that auto-iterates through all pages.

    Use as an iterator to transparently fetch all pages:
        for item in client.listings.list():
            print(item.name)

    Or access the current page directly:
        page = client.listings.list()
        page.data       # list of items
        page.has_more   # bool
        page.cursor     # next page cursor
    """

    object: str = "list"

    def __init__(
        self,
        *,
        data: list[T],
        has_more: bool,
        total_count: int,
        cursor: str | None,
        client: SyncClient,
        path: str,
        params: dict[str, Any],
        model: type[T],
    ) -> None:
        self.data = data
        self.has_more = has_more
        self.total_count = total_count
        self.cursor = cursor
        self._client = client
        self._path = path
        self._params = params
        self._model = model

    def __iter__(self) -> Iterator[T]:
        page = self
        while True:
            yield from page.data
            if not page.has_more or page.cursor is None:
                break
            page = self._client.get_page(
                path=self._path,
                params={**self._params, "cursor": page.cursor},
                model=self._model,
            )

    def to_list(self, *, limit: int | None = None) -> list[T]:
        """Collect all items across pages into a list.

        Args:
            limit: If provided, stop after collecting this many items.

        Returns:
            A list of all items (up to ``limit`` if given).
        """
        items: list[T] = []
        for item in self:
            items.append(item)
            if limit is not None and len(items) >= limit:
                break
        return items


class AsyncCursorPage(Generic[T]):
    """Async version of SyncCursorPage. Use with `async for`."""

    object: str = "list"

    def __init__(
        self,
        *,
        data: list[T],
        has_more: bool,
        total_count: int,
        cursor: str | None,
        client: AsyncClient,
        path: str,
        params: dict[str, Any],
        model: type[T],
    ) -> None:
        self.data = data
        self.has_more = has_more
        self.total_count = total_count
        self.cursor = cursor
        self._client = client
        self._path = path
        self._params = params
        self._model = model

    async def __aiter__(self) -> AsyncIterator[T]:
        page = self
        while True:
            for item in page.data:
                yield item
            if not page.has_more or page.cursor is None:
                break
            page = await self._client.get_page(
                path=self._path,
                params={**self._params, "cursor": page.cursor},
                model=self._model,
            )

    async def to_list(self, *, limit: int | None = None) -> list[T]:
        """Collect all items across pages into a list (async).

        Args:
            limit: If provided, stop after collecting this many items.

        Returns:
            A list of all items (up to ``limit`` if given).
        """
        items: list[T] = []
        async for item in self:
            items.append(item)
            if limit is not None and len(items) >= limit:
                break
        return items
