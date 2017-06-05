
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
        self.url = url.rstrip("/")

        self.session = requests.Session()

    def get(self, route, **kwargs):
        return self._generic_http_method_request(
            "get", route, **kwargs
        )

    def post(self, route, **kwargs):
        return self._generic_http_method_request(
            "post", route, **kwargs
        )

    def put(self, route, **kwargs):
        return self._generic_http_method_request(
            "put", route, **kwargs
        )

    def patch(self, route, **kwargs):
        return self._generic_http_method_request(
            "patch", route, **kwargs
        )

    def delete(self, route, **kwargs):
        return self._generic_http_method_request(
            "delete", route, **kwargs
        )

    def _generic_http_method_request(self, method, route, **kwargs):
        http_method = getattr(self.session, method)
        req_url = urljoin(self.url, route.lstrip("/"))

        if self.username and self.password:
            response = http_method(
                req_url, auth=(self.username, self.password), **kwargs
            )
        elif self.token:
            response = http_method(
                req_url, auth=_HTTPTokenAuth(self.token), **kwargs
            )
        else:
            response = http_method(req_url, **kwargs)

        return self._handle_json_response(response)

    def build_model_url(self, app_name, model):
        return urljoin(self.url, self.build_model_route(app_name, model))

    def build_model_route(self, app_name, model):
        return "api/{}/{}/".format(app_name, model)

    def _handle_json_response(self, response):
        response.raise_for_status()
        json_response = response.json()
        return json_response
