import requests

from .mixin import (
    Magento2ClientMixin,
)


import logging
log = logging.getLogger(__name__)


class Magento2Stores(Magento2ClientMixin):
    def get_store_views(self):
        stores = self.perform_request(
            method=requests.get,
            url=f"{self.url}/rest/{self.channel}/V1/store/storeViews"
        )

        return stores

    def get_websites(self):
        websites = self.perform_request(
            method=requests.get,
            url=f"{self.url}/rest/{self.channel}/V1/store/websites"
        )

        return websites
