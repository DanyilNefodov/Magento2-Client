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


ERROR_NO_IMAGE_WAS_FOUND = "No image with the provided ID was found"


class Magento2ProductMedia(Magento2ClientMixin):
    def get_media(self, sku, download_images: bool = True):
        gallery = self.perform_request(
            method=requests.get,
            url=f"{self.url}/rest/all/V1/products/{encode_special_symbols(sku)}/media"
        )

        if not isinstance(gallery, list):
            gallery = []

        if download_images:
            for index, media in enumerate(gallery):
                image_url = False

                if isinstance(media, dict) and media.get("extension_attributes", {}).get("image_url", False):
                    image_url = media.get("extension_attributes", {}).get("image_url")

                if not image_url:
                    image_url = f"{self.url}/media/catalog/product/{media.get('file')[1:]}"

                image_content = self.perform_request(
                    method=requests.get,
                    url=image_url
                )
                if not image_content:
                    log.exception(f"AttributeError in {sku}:\nindex: {index}\nmedia: {media}")
                    image_content = ""

                try:
                    gallery[index]['content'] = image_content
                except IndexError:
                    log.exception(f"IndexError in {sku}:\nindex: {index}\ngallery: {gallery}\nmedia: {media}\ncontent: {image_content}")

        return gallery

    def post_media(self, media: dict, product_code: str):
        content = self.perform_request(
            method=requests.post,
            url=f"{self.url}/rest/all/V1/products/{encode_special_symbols(product_code)}/media",
            data=json.dumps(media)
        )

        try:
            if not isinstance(content, dict) and content.isdigit():
                return (content, "Success")
        except AttributeError as e:
            log.exception(f"AttributeError in Post Media:\n{e}")
        return (content, "Success")

    def put_media(self, media: dict, product_code: str):
        try:
            entry_id = media.get('id')
        except (KeyError, AttributeError):
            entry_id = None

        content = self.perform_request(
            method=requests.put,
            url=f"{self.url}/rest/all/V1/products/{encode_special_symbols(product_code)}/media/{entry_id}",
            data=json.dumps(media)
        )

        if isinstance(content, dict) and ERROR_NO_IMAGE_WAS_FOUND in content.get("message"):
            return self.post_media(media, product_code)

        return (bool(content), "PUT Media Error")

    def delete_media(self, sku: str, entry_id: int):
        content = self.perform_request(
            method=requests.delete,
            url=f"{self.url}/rest/all/V1/products/{encode_special_symbols(sku)}/media/{entry_id}"
        )

        return bool(content)

    def synchronize_media(self, product_code: str, gallery: list):
        try:
            for existing_media in self.get_media(product_code, download_images=False):
                self.delete_media(product_code, existing_media.get("id"))
            for media_data in gallery:
                self.post_media(media_data, product_code)
        except Exception as error:
            log.exception(f"Synchronize media {product_code}: {error}")
            return (False, f"Synchronize media {product_code}: {error}")
        return (True, "")
