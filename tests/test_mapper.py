
import pytest
import requests_mock

from netboxapi import NetboxMapper, NetboxAPI
from netboxapi.exceptions import ForbiddenAsChildError


class TestNetboxMapper():
    url = "http://localhost/api"
    api = NetboxAPI(url)
    test_app_name = "test_app_name"
    test_model = "test_model"

    @pytest.fixture()
    def mapper(self):
        return NetboxMapper(self.api, self.test_app_name, self.test_model)

    def test_get(self, mapper):
        url = self.get_mapper_url(mapper)
        expected_attr = {
            "count": 1, "next": None, "previous": None,
            "results": [{"id": 1, "name": "test"}]
        }
        with requests_mock.Mocker() as m:
            m.register_uri("get", url, json=expected_attr)
            child_mapper = next(mapper.get())

        for key, val in expected_attr["results"][0].items():
            assert getattr(child_mapper, key) == val

    def test_get_submodel(self, mapper):
        url = self.get_mapper_url(mapper)
        expected_attr = {
            "count": 1, "next": None, "previous": None,
            "results": [{"id": 1, "name": "first_model"}]
        }

        with requests_mock.Mocker() as m:
            m.register_uri(
                "get", url,
                json={
                    "count": 1, "next": None, "previous": None,
                    "results": [{"id": 1}]
                }
            )
            parent_mapper = next(mapper.get())
            m.register_uri(
                "get", url + "{}/{}/".format(parent_mapper.id, "submodel"),
                json=expected_attr
            )
            submodel_mapper = next(parent_mapper.get("submodel"))

        for key, val in expected_attr["results"][0].items():
            assert getattr(submodel_mapper, key) == val

    def test_post(self, mapper):
        url = self.get_mapper_url(mapper)

        with requests_mock.Mocker() as m:
            received_req = m.register_uri(
                "post", url, json=self.update_or_create_resource_json_callback
            )
            child_mapper = mapper.post(name="testname")

        assert child_mapper.id == 1
        assert child_mapper.name == "testname"

    def test_put(self, mapper):
        child_mapper = self.get_child_mapper(mapper)
        url = self.get_mapper_url(child_mapper) + "{}/".format(child_mapper.id)
        with requests_mock.Mocker() as m:
            received_req = m.register_uri(
                "put", url, json=self.update_or_create_resource_json_callback
            )
            child_mapper.name = "another testname"
            updated_child_mapper = child_mapper.put()

        assert updated_child_mapper.name == "another testname"

    def update_or_create_resource_json_callback(self, request, context):
        json = request.json()
        json["id"] = 1
        return json

    def get_child_mapper(self, mapper):
        url = self.get_mapper_url(mapper)
        expected_attr = {
            "count": 1, "next": None, "previous": None,
            "results": [{"id": 1, "name": "test"}]
        }
        with requests_mock.Mocker() as m:
            m.register_uri("get", url, json=expected_attr)
            child_mapper = next(mapper.get())

        return child_mapper

    def test_delete(self, mapper):
        url = self.get_mapper_url(mapper)
        with requests_mock.Mocker() as m:
            m.register_uri("delete", url + "1/")
            req = mapper.delete(1)

        assert req.status_code == 200

    def test_delete_without_id(self, mapper):
        with pytest.raises(ValueError):
            mapper.delete()

    def test_delete_from_child(self, mapper):
        url = self.get_mapper_url(mapper) + "1/"

        with requests_mock.Mocker() as m:
            m.register_uri(
                "get", url, json={"id": 1}
            )
            obj_mapper = next(mapper.get(1))

        with requests_mock.Mocker() as m:
            m.register_uri("delete", url + "1/")
            response = obj_mapper.delete()

        assert response.status_code == 200

    def test_delete_other_id_from_child(self, mapper):
        url = self.get_mapper_url(mapper) + "1/"

        with requests_mock.Mocker() as m:
            m.register_uri(
                "get", url, json={"id": 1}
            )
            obj_mapper = next(mapper.get(1))

        with pytest.raises(ForbiddenAsChildError):
            obj_mapper.delete(1)

    def get_mapper_url(self, mapper):
        return mapper.netbox_api.build_model_url(
            mapper.__app_name__, mapper.__model__
        )
