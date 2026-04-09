"""CheckoutField input builder — type-safe checkout schema construction."""

from __future__ import annotations

from typing import Any


class CheckoutField:
    """Input builder for checkout schema fields. Use factory methods — do not instantiate directly.

    Examples::

        CheckoutField.text("notes", label="Special Instructions")
        CheckoutField.select("size", label="Size", options=["S", "M", "L"])
        CheckoutField.date("delivery_date", label="Preferred Date")
    """

    __slots__ = ("_key", "_type", "_label", "_required", "_options", "_sort_order")

    def __init__(self) -> None:
        raise TypeError("Use factory methods: CheckoutField.text(), .select(), .date()")

    @classmethod
    def text(cls, key: str, *, label: str, required: bool = True, sort_order: int = 0) -> CheckoutField:
        """Create a free-text checkout field.

        Args:
            key: Unique field key — becomes the key in ``order.checkout_data``.
            label: Label shown to the buyer at checkout.
            required: Whether the field must be filled (default True).
            sort_order: Display order — lower values shown first (default 0).
        """
        inst = object.__new__(cls)
        inst._key = key
        inst._type = "text"
        inst._label = label
        inst._required = required
        inst._options = None
        inst._sort_order = sort_order
        return inst

    @classmethod
    def select(
        cls,
        key: str,
        *,
        label: str,
        options: list[str],
        required: bool = True,
        sort_order: int = 0,
    ) -> CheckoutField:
        """Create a dropdown select checkout field.

        Args:
            key: Unique field key — becomes the key in ``order.checkout_data``.
            label: Label shown to the buyer at checkout.
            options: List of selectable options (e.g. ``["S", "M", "L"]``).
            required: Whether the field must be filled (default True).
            sort_order: Display order — lower values shown first (default 0).
        """
        inst = object.__new__(cls)
        inst._key = key
        inst._type = "select"
        inst._label = label
        inst._required = required
        inst._options = options
        inst._sort_order = sort_order
        return inst

    @classmethod
    def date(cls, key: str, *, label: str, required: bool = True, sort_order: int = 0) -> CheckoutField:
        """Create a date picker checkout field.

        Args:
            key: Unique field key — becomes the key in ``order.checkout_data``.
            label: Label shown to the buyer at checkout.
            required: Whether the field must be filled (default True).
            sort_order: Display order — lower values shown first (default 0).
        """
        inst = object.__new__(cls)
        inst._key = key
        inst._type = "date"
        inst._label = label
        inst._required = required
        inst._options = None
        inst._sort_order = sort_order
        return inst

    def to_api_body(self) -> dict[str, Any]:
        """Serialize to API request body dict."""
        body: dict[str, Any] = {
            "key": self._key,
            "type": self._type,
            "label": self._label,
            "required": self._required,
            "sort_order": self._sort_order,
        }
        if self._options is not None:
            body["options"] = self._options
        return body

    def __repr__(self) -> str:
        return f"CheckoutField.{self._type}({self._key!r}, label={self._label!r})"
