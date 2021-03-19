import requests

from .mixin import (
    Magento2ClientMixin,
)


import logging
log = logging.getLogger(__name__)


class Magento2Stock(Magento2ClientMixin):
    def get_stock(self, sku: str):
        stock = self.perform_request(
            method=requests.get,
            url=f"{self.url}/rest/{self.channel}/V1/stockItems/{sku}"
        )

        return stock
