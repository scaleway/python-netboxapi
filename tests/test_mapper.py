
import pytest
import requests_mock

from netboxapi import NetboxMapper, NetboxAPI


class TestNetboxMapper():
    url = "http://localhost/"
    api = NetboxAPI(url)
    test_app_name = "test_app_name"
    test_model = "test_model"

    @pytest.fixture()
    def mapper(self):
        return NetboxMapper(self.api, self.test_app_name, self.test_model)

    def test_get(self, mapper):
        url = mapper._url
        expected_json = {"id": 1, "name": "test"}
        with requests_mock.Mocker() as m:
            m.register_uri("get", url, json=expected_json)
            response = mapper.get()

    def test_get_submodel(self, mapper):
        url = mapper._url.rstrip("/") + "/submodel"
        expected_json = {"id": 1, "name": "test"}
        with requests_mock.Mocker() as m:
            m.register_uri("get", url, json=expected_json)
            response = mapper.get("submodel")
