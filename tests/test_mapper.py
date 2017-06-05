
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
        url = self.get_mapper_url(mapper)
        expected_attr = {"id": 1, "name": "test"}
        with requests_mock.Mocker() as m:
            m.register_uri("get", url, json=expected_attr)
            child_mapper = next(mapper.get())

        for key, val in expected_attr.items():
            assert getattr(child_mapper, key) == val

    def test_get_submodel(self, mapper):
        url = self.get_mapper_url(mapper)
        expected_attr = {"id": 1, "name": "first_model"}

        with requests_mock.Mocker() as m:
            m.register_uri("get", url, json={"id": 1, })
            parent_mapper = next(mapper.get())
            m.register_uri("get", url + "submodel", json=expected_attr)
            submodel_mapper = next(parent_mapper.get("submodel"))

        for key, val in expected_attr.items():
            assert getattr(submodel_mapper, key) == val

    def get_mapper_url(self, mapper):
        return mapper.netbox_api.build_model_url(mapper.app_name, mapper.model)
