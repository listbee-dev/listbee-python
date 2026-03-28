# listbee

Official Python SDK for the [ListBee API](https://listbee.so) — one API call to sell and deliver digital content.

## Install

```bash
pip install listbee
```

## Quick Start

```python
from listbee import ListBee

client = ListBee(api_key="lb_...")

# List your listings
listings = client.listings.list()
for listing in listings:
    print(listing.slug, listing.title)
```

## Links

- [Documentation](https://docs.listbee.so)
- [Changelog](CHANGELOG.md)
- [PyPI](https://pypi.org/project/listbee/)
