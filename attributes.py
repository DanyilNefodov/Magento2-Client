import requests
import json

from .mixin import (
    Magento2ClientMixin,
)


import logging
log = logging.getLogger(__name__)


ERROR_OPTION_ALREADY_NOT_EXISTS = "attribute option label \"%1\" is already exists."
ERROR_OPTION_DOES_NOT_EXISTS = "Option with id"


class Magento2Attributes(Magento2ClientMixin):
    def get_attributes(self):
        content = self.perform_request(
            method=requests.get,
            url=f"{self.url}/rest/{self.channel}/V1/products/attributes",
            params={
                'searchCriteria': "[0]"
            }
        )

        return content.get("items", [])

    def get_attribute_options(self, attribute_code: str, has_swatch: bool = False):
        content = self.perform_request(
            method=requests.get,
            url=f"{self.url}/rest/{self.channel}/{'V2' if has_swatch else 'V1'}/products/attributes/{attribute_code}/options"
        )

        return content

    def post_attribute_option(self, option: dict, attribute_code: str):
        content = self.perform_request(
            method=requests.post,
            url=f"{self.url}/rest/{self.channel}/V1/products/attributes/{attribute_code}/options",
            data=json.dumps({'option': option})
        )

        if isinstance(content, dict):
            if ERROR_OPTION_ALREADY_NOT_EXISTS in content.get('message', ''):
                return (False, "Magento already has such attribute option.")

        try:
            aid = int(content.split('_')[-1])
        except (ValueError, KeyError, ):
            return (False, f"Magento returned error:\nPOST Attribute Option:\n{content}")
        except (AttributeError, ):
            if isinstance(content, int) or isinstance(content, str) and content.isdigit():
                aid = int(content)
            else:
                return (False, f"Magento returned error:\nPOST Attribute Option:\n{content}")

        return (aid, "Success")

    def put_attribute_option(self, option: dict, attribute_code: str, option_id: int):
        if option_id:
            content = self.perform_request(
                method=requests.put,
                url=f"{self.url}/rest/{self.channel}/V1/products/attributes/{attribute_code}/options/{option_id}",
                data=json.dumps({'option': option})
            )
        else:
            content = dict(message=ERROR_OPTION_DOES_NOT_EXISTS)

        if isinstance(content, dict):
            if content.get('message', '').startswith(ERROR_OPTION_DOES_NOT_EXISTS):
                return self.post_attribute_option(option, attribute_code)

        try:
            option_id = int(content.split('_')[-1])
        except (ValueError, KeyError, ):
            return (False, f"Magento returned error:\nPUT Attribute Option:\n{content}")
        except (AttributeError, ):
            if isinstance(content, int) or isinstance(content, str) and content.isdigit():
                option_id = int(content)
            else:
                return (False, f"Magento returned error:\nPUT Attribute Option:\n{content}")

        return (option_id, "Success")

    def delete_attribute_option(self, attribute_code: str, attribute_option_id: int):
        content = self.perform_request(
            method=requests.delete,
            url=f"{self.url}/rest/{self.channel}/V1/products/attributes/{attribute_code}/options/{attribute_option_id}"
        )

        return (True, "Success") if bool(content) else (False, f"Magento returned error: {content}")
