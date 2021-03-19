import datetime
import requests
import json


import logging
log = logging.getLogger(__name__)


ERROR_CUSTOMER_IS_INCORRECT = "The account sign-in was incorrect or your account is disabled temporarily. Please wait and try again later."
ERROR_CUSTOMER_IS_NOT_AUTHORIZED = "The consumer isn't authorized to access"


class Magento2ClientMixin():
    def __init__(self, synchronization):
        self.synchronization_id = getattr(synchronization, 'id')
        self.url = getattr(synchronization, 'url')
        self.login = getattr(synchronization, 'login')
        self.password = getattr(synchronization, 'password')
        self.channel = getattr(synchronization, 'channel', 'all')
        self.token = self.get_token()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # If api has token destruction endpoint
        pass

    def get_token(self):
        try:
            responce = requests.post(
                f"{self.url}/rest/{self.channel}/V1/integration/admin/token",
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
                },
                params={
                    'username': self.login,
                    'password': self.password,
                },
                verify=False
            )
        except requests.exceptions.ConnectionError:
            return False

        try:
            content = json.loads(responce.content)
        except (json.decoder.JSONDecodeError, UnicodeDecodeError):
            log.exception(f"M2 Token error: {responce.content}")
            content = ''

        if not isinstance(content, str) and content.get("message", "") == ERROR_CUSTOMER_IS_INCORRECT:
            return False
        return content

    def perform_request(self, method, url: str, headers: dict = {}, params: dict = {}, data: dict = {}, ssl_verification=True, turn_on_log=True):
        REQUIRED_HEADERS = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
        }
        try:
            responce = method(url,
                    headers=dict(**headers, **REQUIRED_HEADERS),
                    params=params,
                    data=data,
                    verify=ssl_verification
                )
        except requests.exceptions.ConnectionError:
            return {}

        try:
            content = json.loads(responce.content)
        except (json.decoder.JSONDecodeError, UnicodeDecodeError):
            content = responce.content

        try:
            content_to_log = json.dumps(content, indent=4)
        except Exception:
            content_to_log = content

        try:
            data_to_log = json.dumps(json.loads(data), indent=4)
        except Exception:
            data_to_log = data

        if turn_on_log:
            ####################### Logging M2 requests ##########################
            log.debug(f"\n\nTime: {datetime.datetime.now().strftime('%m/%d/%Y, %H:%M:%S')}\nMethod: {method}\nUrl: {url}\nHeaders: {dict(**headers, **REQUIRED_HEADERS)}\nParams: {params}\nData: {data_to_log}\nResponce code: {responce.status_code}\nResponce content: {content_to_log}\n\n")
            ####################### Logging M2 requests ##########################

        if responce.status_code != 200:
            return content

        try:
            if content.get("message", "").startswith(ERROR_CUSTOMER_IS_NOT_AUTHORIZED):
                self.token = self.get_token()
                if not self.token:
                    return {}

                return self.perform_request(method, url, headers, params, data)
        except json.decoder.JSONDecodeError:
            log.exception(f"request: {method} {url}\nheaders: {headers}\nparams: {params}\ndata: {data}\n\nresponce {responce.status_code}: {content}")
            return {}
        except (AttributeError, ):
            pass

        return content
