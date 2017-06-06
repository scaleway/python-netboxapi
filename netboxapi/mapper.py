
from .api import NetboxAPI
from .exceptions import ForbiddenAsChildError


class NetboxMapper():
    def __init__(self, netbox_api, app_name, model, route=None):
        self.netbox_api = netbox_api
        self.__app_name__ = app_name
        self.__model__ = model
        self.__upstream_attrs__ = []

        self._route = (
            route or
            self.netbox_api.build_model_route(
                self.__app_name__, self.__model__
            )
        ).rstrip("/") + "/"

    def get(self, *args, **kwargs):
        """
        Get netbox objects

        Use args and kwargs as filters: all *args items are joined with "/",
        and kwargs are use as data parameter. It is then used to build the
        request uri

        Examples:
            >>> netbox_mapper.__app_name__ = "dcim"
            >>> netbox_mapper.__model__ = "sites"
            >>> netbox_mapper.get("1", "racks", q="name_to_filter")

            Will do a request to "/api/dcim/sites/1/racks/?q=name_to_filter"
        """
        if args:
            route = self._route + "/".join(str(a) for a in args) + "/"
        else:
            route = self._route

        new_mappers_dict = self.netbox_api.get(route, data=kwargs)
        if isinstance(new_mappers_dict, dict):
            new_mappers_dict = [new_mappers_dict]
        for d in new_mappers_dict:
            yield self._build_new_mapper_from(d, route)

    def post(self, **json):
        new_mapper_dict = self.netbox_api.post(self._route, json=json)
        route = self._route + "{}/".format(new_mapper_dict["id"])

        return self._build_new_mapper_from(new_mapper_dict, route)

    def put(self):
        assert getattr(self, "id", None) is not None, "self.id does not exist"

        return self.netbox_api.put(self._route, json=self.to_dict())

    def to_dict(self):
        return {a: getattr(self, a, None) for a in self.__upstream_attrs__}

    def delete(self, id=None):
        """
        Delete netbox object or self

        :param id: id to delete. Only root mappers can delete any id, so if
            self has already an id, it will be considered as a child (a single
            object in netbox) and will not be able to delete other ID than
            itself. In this case, specifying an ID will conflict and raise a
            ForbiddenAsChildError
        """
        if id is not None and getattr(self, "id", None) is not None:
            raise ForbiddenAsChildError(
                "Cannot specify an ID to delete when self is a mapper child "
                "and has an ID"
            )
        elif id is None and getattr(self, "id", None) is None:
            raise ValueError("Delete needs an id when self.id does not exist")

        delete_route = self._route + "{}/".format(id) if id else self._route
        return self.netbox_api.delete(delete_route)

    def _build_new_mapper_from(self, mapper_attributes, new_route):
        mapper = type(self)(
            self.netbox_api, self.__app_name__, self.__model__, new_route
        )
        mapper.__upstream_attrs__ = list(mapper_attributes.keys())
        for attr, val in mapper_attributes.items():
            setattr(mapper, attr, val)

        return mapper
