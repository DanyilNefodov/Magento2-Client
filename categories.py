import requests
import json

from .mixin import (
    Magento2ClientMixin,
)


import logging
log = logging.getLogger(__name__)


ERROR_CATEGORY_ALREADY_NOT_EXISTS = "\"%1\" is already exists."
ERROR_CATEGORY_DOES_NOT_EXISTS = "Could not save category"
ERROR_PARENT_CATEGORY_NOT_EXISTS = "No such entity with id"


class Magento2Categories(Magento2ClientMixin):
    def get_categories(self):
        categories = self.perform_request(
            method=requests.get,
            url=f"{self.url}/rest/{self.channel}/V1/categories/list",
            params={
                'searchCriteria': "[0]"
            }
        ).get("items", [])

        for index, category in enumerate(categories):
            extension_attributes = category.pop('extension_attributes', {})
            custom_attributes = category.pop('custom_attributes', {})

            for key, extension_attribute in extension_attributes.items():
                category[key] = extension_attribute

            for custom_attribute in custom_attributes:
                category[custom_attribute.get('attribute_code')] = custom_attribute.get('value')

            categories[index] = category

        return categories

    def get_category(self, category_id: int):
        category = self.perform_request(
            method=requests.get,
            url=f"{self.url}/rest/{self.channel}/V1/categories/{category_id}"
        )

        extension_attributes = category.pop('extension_attributes', {})
        custom_attributes = category.pop('custom_attributes', {})

        for custom_attribute in custom_attributes:
            category[custom_attribute.get('attribute_code')] = custom_attribute.get('value')

        for key, extension_attribute in extension_attributes.items():
            category[key] = extension_attribute

        return category

    def post_category(self, category: dict):
        try:
            category.pop('id')
        except KeyError:
            pass

        if not category.get('parent_id', True):
            category.pop('parent_id')

        content = self.perform_request(
            method=requests.post,
            url=f"{self.url}/rest/{self.channel}/V1/categories",
            data=json.dumps({"category": category})
        )

        if isinstance(content, dict):
            if ERROR_CATEGORY_ALREADY_NOT_EXISTS in content.get('message', ''):
                return (False, "Magento already has such category.")
            if ERROR_PARENT_CATEGORY_NOT_EXISTS in content.get('message', ''):
                return (False, "Parent category not exists.")

        try:
            cid = content['id']
        except (AttributeError, KeyError, TypeError):
            return (False, f"Magento returned error:\nPOST Category:\n{content}")

        return (cid, "Success")

    def put_category(self, category: dict):
        try:
            cid = category.pop('id')
        except (AttributeError, KeyError):
            cid = None

        if not cid:
            return self.post_category(category)

        content = self.perform_request(
            method=requests.put,
            url=f"{self.url}/rest/{self.channel}/V1/categories/{cid}",
            data=json.dumps({"category": category})
        )

        if isinstance(content, dict):
            if content.get('message', '').startswith(ERROR_CATEGORY_DOES_NOT_EXISTS) or content.get('message', '').startswith(ERROR_PARENT_CATEGORY_NOT_EXISTS):
                return self.post_category(category)
        if isinstance(content, bytes):  # Temporary decision depence on M2 exception functionality
            try:
                content = content.decode("utf-8")
                if ERROR_PARENT_CATEGORY_NOT_EXISTS in content[1:].split(",")[0]:
                    return self.post_category(category)
                else:
                    raise IndexError
            except (UnicodeDecodeError, IndexError):
                return (False, f"Magento returned error: {content}")

        try:
            cid = content['id']
        except (AttributeError, KeyError, TypeError):
            return (False, f"Magento returned error:\nPUT Category\n{content}")

        return (cid, "Success")

    def delete_category(self, entity_id: int):
        content = self.perform_request(
            method=requests.delete,
            url=f"{self.url}/rest/{self.channel}/V1/categories/{entity_id}"
        )

        return (True, "Success") if bool(content) else (False, f"Magento returned error: {content}")
