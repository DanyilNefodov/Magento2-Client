import requests
import json

from .mixin import (
    Magento2ClientMixin,
)
from ...utils.helpers import (
    encode_special_symbols,
)


import logging
log = logging.getLogger(__name__)


ERROR_PRODUCT_DOES_NOT_EXISTS = "The Product with the \"%1\" SKU doesn\'t exist."
ERROR_MAGENTO_FATAL = "<b>Fatal error</b>"


class Magento2Products(Magento2ClientMixin):
    def get_products(self, search_params: dict):
        content = self.perform_request(
            method=requests.get,
            url=f"{self.url}/rest/{self.channel}/V1/products",
            params=search_params
        )

        try:
            products = content.get("items", [])
        except AttributeError:
            log.exception(content)
            return []

        for index, product in enumerate(products):
            extension_attributes = product.pop('extension_attributes', {})
            custom_attributes = product.pop('custom_attributes', {})

            for key, extension_attribute in extension_attributes.items():
                product[key] = extension_attribute
            product.update(product.pop("stock_item", {}))

            for custom_attribute in custom_attributes:
                product[custom_attribute.get('attribute_code')] = custom_attribute.get('value')

            products[index] = product

        return products

    def get_typed_products(self, type_id: str, page_size: int = 500, current_page: int = 0):
        params = {
            'searchCriteria[pageSize]': page_size,
            'searchCriteria[currentPage]': current_page,
            'searchCriteria[filterGroups][0][filters][0][conditionType]': 'eq',
            'searchCriteria[filterGroups][0][filters][0][field]': 'type_id',
            'searchCriteria[filterGroups][0][filters][0][value]': type_id,
            'searchCriteria[filterGroups][1][filters][0][conditionType]': 'eq',
            'searchCriteria[filterGroups][1][filters][0][field]': 'status',
            'searchCriteria[filterGroups][1][filters][0][value]': 1,
        }

        return self.get_products(params)

    def get_product(self, sku: str):
        product = self.perform_request(
            method=requests.get,
            url=f"{self.url}/rest/{self.channel}/V1/products/{encode_special_symbols(sku)}"
        )

        extension_attributes = product.pop('extension_attributes', {})
        custom_attributes = product.pop('custom_attributes', {})

        for key, extension_attribute in extension_attributes.items():
            product[key] = extension_attribute
        product.update(product.pop("stock_item", {}))

        for custom_attribute in custom_attributes:
            product[custom_attribute.get('attribute_code')] = custom_attribute.get('value')

        return product

    def post_product(self, product: dict):
        return self.put_product(product, True)

    def put_product(self, product: dict, new: bool = False):
        if not product.get("id"):
            new = True

        if not new:
            method = requests.put
            url = f"{self.url}/rest/{self.channel}/V1/products/{encode_special_symbols(product.get('sku'))}"
        else:
            method = requests.post
            url = f"{self.url}/rest/{self.channel}/V1/products"

        content = self.perform_request(
            method=method,
            url=url,
            data=json.dumps({"product": product, "saveOptions": False})
        )

        if isinstance(content, dict) and content.get('message') == ERROR_MAGENTO_FATAL or isinstance(content, dict) and ERROR_MAGENTO_FATAL in content or isinstance(content, bytes) and ERROR_MAGENTO_FATAL in content.decode():
            return (False, f"Magento returned fatal error: {content}")

        try:
            pid = content['id']
        except (KeyError, TypeError):
            return (False, f"Magento returned error: {content}")
        return (pid, True)

    def set_special_prices(self, prices: dict):
        responce = self.perform_request(
            method=requests.post,
            url=f"{self.url}/rest/{self.channel}/V1/products/special-price",
            data=json.dumps(prices)
        )

        return responce
