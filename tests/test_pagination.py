from unittest.mock import MagicMock

from pydantic import BaseModel

from listbee._pagination import SyncCursorPage


class FakeItem(BaseModel):
    name: str


class TestSyncCursorPage:
    def test_iterate_single_page(self):
        page = SyncCursorPage(
            data=[FakeItem(name="a"), FakeItem(name="b")],
            has_more=False,
            cursor=None,
            client=MagicMock(),
            path="/test",
            params={},
            model=FakeItem,
        )
        names = [item.name for item in page]
        assert names == ["a", "b"]

    def test_iterate_multiple_pages(self):
        mock_client = MagicMock()
        page2 = SyncCursorPage(
            data=[FakeItem(name="c")],
            has_more=False,
            cursor=None,
            client=mock_client,
            path="/test",
            params={},
            model=FakeItem,
        )
        mock_client.get_page.return_value = page2

        page1 = SyncCursorPage(
            data=[FakeItem(name="a"), FakeItem(name="b")],
            has_more=True,
            cursor="cursor_abc",
            client=mock_client,
            path="/test",
            params={"limit": 2},
            model=FakeItem,
        )
        names = [item.name for item in page1]
        assert names == ["a", "b", "c"]
        mock_client.get_page.assert_called_once_with(
            path="/test",
            params={"limit": 2, "cursor": "cursor_abc"},
            model=FakeItem,
        )

    def test_iterate_empty_page(self):
        page = SyncCursorPage(
            data=[],
            has_more=False,
            cursor=None,
            client=MagicMock(),
            path="/test",
            params={},
            model=FakeItem,
        )
        assert list(page) == []

    def test_data_attribute_access(self):
        page = SyncCursorPage(
            data=[FakeItem(name="x")],
            has_more=True,
            cursor="next",
            client=MagicMock(),
            path="/test",
            params={},
            model=FakeItem,
        )
        assert len(page.data) == 1
        assert page.has_more is True
        assert page.cursor == "next"
        assert page.object == "list"
