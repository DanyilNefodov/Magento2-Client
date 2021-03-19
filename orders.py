import requests
import json

from .mixin import (
    Magento2ClientMixin,
)


import logging
log = logging.getLogger(__name__)


class Magento2Orders(Magento2ClientMixin):
    def get_orders(self, page_size: int = 500, current_page: int = 0):
        content = self.perform_request(
            method=requests.get,
            url=f"{self.url}/rest/{self.channel}/V1/orders",
            params={
                "searchCriteria[pageSize]": page_size,
                "searchCriteria[currentPage]": current_page,
            }
        )

        return content.get("items", [])

    def get_order(self, order_id: int):
        order = self.perform_request(
            method=requests.get,
            url=f"{self.url}/rest/{self.channel}/V1/orders/{order_id}"
        )

        return order

    def get_shipments(self, order_id: int):
        shipments = self.perform_request(
            method=requests.get,
            url=f"{self.url}/rest/{self.channel}/V1/orders/{order_id}"
        )

        return shipments
