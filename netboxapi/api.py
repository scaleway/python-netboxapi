
import requests
from urllib.parse import urljoin


class _HTTPTokenAuth(requests.auth.AuthBase):
    """HTTP Basic Authentication with token."""

    def __init__(self, token):
        self.token = token

    def __eq__(self, other):
        return self.token == getattr(other, 'token', None)

    def __ne__(self, other):
        return not self == other

    def __call__(self, r):
        r.headers["Authorization"] = "Token {}".format(self.token)
        return r


class NetboxAPI():
    def __init__(self, url, username=None, password=None, token=None):
        self.username = username
        self.password = password
        self.token = token
        self.url = url.rstrip('/')

        self.session = requests.Session()

    def get(self, url, **kwargs):
        return self._generic_http_method_request(
            "get", url, **kwargs
        )

    def post(self, url, **kwargs):
        return self._generic_http_method_request(
            "post", url, **kwargs
        )

    def put(self, url, **kwargs):
        return self._generic_http_method_request(
            "put", url, **kwargs
        )

    def patch(self, url, **kwargs):
        return self._generic_http_method_request(
            "patch", url, **kwargs
        )

    def delete(self, url, **kwargs):
        return self._generic_http_method_request(
            "delete", url, **kwargs
        )

    def _generic_http_method_request(self, method, url, **kwargs):
        http_method = getattr(self.session, method)

        if self.username and self.password:
            response = http_method(
                url, auth=(self.username, self.password), **kwargs
            )
        elif self.token:
            response = http_method(
                url, auth=_HTTPTokenAuth(self.token), **kwargs
            )
        else:
            response = http_method(url, **kwargs)

        return self._handle_json_response(response)

    def build_model_url(self, app_name, model):
        return urljoin(self.url, "api/{}/{}/".format(app_name, model))

    def _handle_json_response(self, response):
        response.raise_for_status()
        json_response = response.json()
        return json_response
