import pytest

from listbee.checkout_field import CheckoutField


class TestCheckoutFieldText:
    def test_text(self):
        f = CheckoutField.text("notes", label="Special Instructions")
        assert f._key == "notes"
        assert f._type == "text"
        assert f._label == "Special Instructions"
        assert f._required is True
        assert f._options is None
        assert f._sort_order == 0

    def test_text_optional(self):
        f = CheckoutField.text("notes", label="Notes", required=False, sort_order=3)
        assert f._required is False
        assert f._sort_order == 3

    def test_text_to_api_body(self):
        f = CheckoutField.text("notes", label="Notes")
        assert f.to_api_body() == {
            "key": "notes",
            "type": "text",
            "label": "Notes",
            "required": True,
            "sort_order": 0,
        }


class TestCheckoutFieldSelect:
    def test_select(self):
        f = CheckoutField.select("size", label="Size", options=["S", "M", "L"])
        assert f._key == "size"
        assert f._type == "select"
        assert f._options == ["S", "M", "L"]

    def test_select_to_api_body(self):
        f = CheckoutField.select("color", label="Color", options=["Red", "Blue"], sort_order=1)
        assert f.to_api_body() == {
            "key": "color",
            "type": "select",
            "label": "Color",
            "required": True,
            "sort_order": 1,
            "options": ["Red", "Blue"],
        }


class TestCheckoutFieldAddress:
    def test_address(self):
        f = CheckoutField.address("shipping", label="Shipping Address")
        assert f._key == "shipping"
        assert f._type == "address"
        assert f._options is None

    def test_address_to_api_body(self):
        f = CheckoutField.address("shipping", label="Shipping Address", sort_order=2)
        assert f.to_api_body() == {
            "key": "shipping",
            "type": "address",
            "label": "Shipping Address",
            "required": True,
            "sort_order": 2,
        }


class TestCheckoutFieldDate:
    def test_date(self):
        f = CheckoutField.date("delivery", label="Preferred Date")
        assert f._key == "delivery"
        assert f._type == "date"
        assert f._options is None

    def test_date_to_api_body(self):
        f = CheckoutField.date("delivery", label="Preferred Date", required=False)
        assert f.to_api_body() == {
            "key": "delivery",
            "type": "date",
            "label": "Preferred Date",
            "required": False,
            "sort_order": 0,
        }


class TestCheckoutFieldConstructor:
    def test_direct_instantiation_raises(self):
        with pytest.raises(TypeError, match="Use factory methods"):
            CheckoutField()

    def test_repr_text(self):
        f = CheckoutField.text("notes", label="Notes")
        assert repr(f) == "CheckoutField.text('notes', label='Notes')"

    def test_repr_select(self):
        f = CheckoutField.select("size", label="Size", options=["S", "M"])
        assert repr(f) == "CheckoutField.select('size', label='Size')"

    def test_repr_address(self):
        f = CheckoutField.address("addr", label="Address")
        assert repr(f) == "CheckoutField.address('addr', label='Address')"

    def test_repr_date(self):
        f = CheckoutField.date("when", label="When")
        assert repr(f) == "CheckoutField.date('when', label='When')"
