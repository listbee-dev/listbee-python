import pytest

from listbee._base_client import SyncClient


@pytest.fixture
def client():
    return SyncClient(api_key="lb_test_key_1234567890abcdef")
