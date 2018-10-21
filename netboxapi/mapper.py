import logging
import re
import requests

from .api import NetboxAPI
from .exceptions import ForbiddenAsChildError, ForbiddenAsPassiveMapperError


logger = logging.getLogger("netboxapi")


class NetboxMapper():
    def __init__(self, netbox_api, app_name, model, route=None):
        self.netbox_api = netbox_api
        self.__app_name__ = app_name
        self.__model__ = model
        self.__upstream_attrs__ = []
        self.__foreign_keys__ = []
        self.__original_foreign_keys_id__ = {}

        #: cache for foreign keys properties.
        self._fk_cache = {}

        self._route = (
            route or
            self.netbox_api.build_model_route(
                self.__app_name__, self.__model__
            )
        ).rstrip("/") + "/"

    def __eq__(self, other):
        if not isinstance(other, NetboxMapper):
            return False

        if other._route != self._route:
            return False

        return self.to_dict() == other.to_dict()

    def get(self, *args, limit=50, **kwargs):
        """
        Get netbox objects

        Use args and kwargs as filters: all *args items are joined with "/",
        and kwargs are use as data parameter. It is then used to build the
        request uri

        Example:
            >>> netbox_mapper.__app_name__ = "dcim"
            >>> netbox_mapper.__model__ = "sites"
            >>> netbox_mapper.get("1", "racks", q="name_to_filter")

            Will do a request to "/dcim/sites/1/racks/?q=name_to_filter"

        Some specific routes will not return objects with ID (this one for
        example: `/ipam/prefixes/{id}/available-prefixes/`). In this case, no
        mapper will be built from the result and it will be yield as received.
        """
        kwargs.setdefault("limit", limit)
        self._replace_params_mappers_by_id(kwargs)

        if args:
            route = self._route + "/".join(str(a) for a in args) + "/"
        else:
            route = self._route

        new_mappers_props = self._iterate_over_get_query(route, kwargs)
        for nm_prop in new_mappers_props:
            try:
                if getattr(self, "id", None) is not None:
                    new_mapper_route = route
                else:
                    new_mapper_route = self._route + "{}/".format(
                        nm_prop["id"]
                    )

                yield self._build_new_mapper_from(nm_prop, new_mapper_route)
            except (KeyError, TypeError):
                # Result objects have no id, cannot build a mapper from them,
                # yield them as received
                yield nm_prop
                yield from new_mappers_props
                return

    def _replace_params_mappers_by_id(self, params):
        """
        Find mappers in a dict and replace them by their id

        Useful to send requests containing a mapper
        """
        for k, v in params.items():
            if isinstance(v, NetboxMapper):
                try:
                    params[k] = v.id
                except AttributeError:
                    raise ValueError("Mapper {} has no id".format(k))

    def _iterate_over_get_query(self, route, params):
        """
        Iterate over a get query and handle possible pagination
        """
        while True:
            response = self.netbox_api.get(route, params=params)
            if "results" in response:
                new_mappers_props = response["results"]
            else:
                if isinstance(response, list):
                    yield from response
                else:
                    yield response
                return

            yield from new_mappers_props

            next_url = response.get("next")
            if next_url:
                params["offset"] = params.get("offset", 0) + params["limit"]
            else:
                return

    def post(self, **json):
        """
        Post a new netbox object

        Use **json to build a json that will be used to package the new object
        atributes. Meant to be use for a "root mapper" (a mapper not directly
        linked to a resource, parent of children mappers).

        Example:
            >>> netbox_mapper.__app_name__ = "dcim"
            >>> netbox_mapper.__model__ = "console-ports"
            >>> netbox_mapper.post(device="A device", cs_port="cs port",
            ...                    name="example")
            <child_mapper>

        :returns: child_mapper: Mapper containing the created object
        """
        self._replace_params_mappers_by_id(json)
        new_mapper_dict = self.netbox_api.post(self._route, json=json)
        try:
            return next(self.get(new_mapper_dict["id"]))
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.debug(
                    "Rare case of weird endpoint where object cannot be fetch "
                    "after POST by using the same endpoint. Returning a "
                    "mapper based on this answer instead of fetching the "
                    "entire object."
                    ""
                    "Do not try to put this mapper as it will fail."
                )
                return self._build_new_mapper_from(
                    new_mapper_dict,
                    self._route + "{}/".format(new_mapper_dict["id"]),
                    passive_mapper=True
                )

    def put(self):
        """
        Update an already existing netbox object

        Use all mapper attributes contained in self.__upstream_attrs__ to build
        a json and send a put request to netbox.

        Example:
            >>> netbox_mapper.__app_name__ = "dcim"
            >>> netbox_mapper.__model__ = "console-ports"
            >>> child_mapper = netbox_mapper.get(1)
            >>> child_mapper.name = "another name"
            >>> child_mapper.put()

        :returns: request_reponse: requests object containing the netbox
                                   response
        """
        assert getattr(self, "id", None) is not None, "self.id does not exist"

        return self.netbox_api.put(self._route, json=self.to_dict())

    def to_dict(self):
        serialize = {}
        foreign_keys = self.__foreign_keys__.copy()
        for a in self.__upstream_attrs__:
            val = getattr(self, a, None)
            if isinstance(val, dict):
                if "value" in val and "label" in val:
                    val = val["value"]
            elif isinstance(val, NetboxMapper):
                foreign_keys.append(a)
                continue

            serialize[a] = val

        for fk in foreign_keys:
            if hasattr(self, "_{}_id".format(fk)):
                serialize[fk] = getattr(self, "_{}_id".format(fk), None)
            else:
                serialize[fk] = self._get_foreign_object_id(
                    getattr(self, fk, None)
                )

        return serialize

    def delete(self, id=None):
        """
        Delete netbox object or self

        Example:
            >>> netbox_mapper.__app_name__ = "dcim"
            >>> netbox_mapper.__model__ = "sites"
            >>> netbox_mapper.delete(1)

            Will delete the `Site` object with `id=1`. It is the same as doing:

            >>> netbox_mapper.__app_name__ = "dcim"
            >>> netbox_mapper.__model__ = "sites"
            >>> child_mapper = netbox_mapper.get(1)
            >>> child_mapper.delete()

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

    def _build_new_mapper_from(
            self, mapper_attributes, new_route, passive_mapper=False
    ):
        cls = NetboxPassiveMapper if passive_mapper else NetboxMapper
        mapper_class = type(
            "NetboxMapper_{}_{}".format(
                re.sub("_|-", "", self.__model__.title()),
                re.sub("_|-", "", "".join(
                    s.title() for s in new_route.split("/")
                ))
            ), (cls,), {}
        )

        mapper = mapper_class(
            self.netbox_api, self.__app_name__, self.__model__, new_route
        )
        mapper.__upstream_attrs__ = []
        mapper.__foreign_keys__ = []
        for attr, val in mapper_attributes.items():
            if isinstance(val, dict) and "id" in val and "url" in val:
                mapper.__foreign_keys__.append(attr)
                mapper.__original_foreign_keys_id__[attr] = val["id"]
                mapper._set_property_foreign_key(attr, val)
            else:
                mapper.__upstream_attrs__.append(attr)
                setattr(mapper, attr, val)

        return mapper

    def _set_property_foreign_key(self, attr, value):
        def get_foreign_object(*args):
            if hasattr(self, "_{}".format(attr)):
                return getattr(self, "_{}".format(attr))

            if attr in self._fk_cache:
                return self._fk_cache[attr]

            url = value["url"]
            route = url.replace(self.netbox_api.url, "", 1).lstrip("/")
            model, app_name, *params = route.split("/")

            fk = list(NetboxMapper(self.netbox_api, model, app_name).get(
                *[p for p in params if p]
            ))
            if not fk:
                fk = None
            elif len(fk) == 1:
                fk = fk[0]

            self._fk_cache[attr] = fk
            return fk

        def setter(cls, value):
            setattr(self, "_{}".format(attr), value)

        def getter_fk_id(*args):
            original_id_condition = (
                not hasattr(self, "_{}".format(attr)) and
                attr in self.__original_foreign_keys_id__
            )

            if original_id_condition:
                return self.__original_foreign_keys_id__[attr]
            else:
                return self._get_foreign_object_id(getattr(self, attr))

        try:
            self._fk_cache.pop(attr)
        except KeyError:
            pass
        setattr(type(self), attr, property(get_foreign_object, setter))
        setattr(
            type(self), "_{}_id".format(attr), property(getter_fk_id)
        )

    def _get_foreign_object_id(self, fk_obj):
        if isinstance(fk_obj, int):
            return fk_obj
        else:
            try:
                # check that fk is iterable
                iter(fk_obj)
                return [getattr(i, "id", None) for i in fk_obj]
            except TypeError:
                return getattr(fk_obj, "id", None)


class NetboxPassiveMapper(NetboxMapper):
    def get(self, *args, **kwargs):
        raise ForbiddenAsPassiveMapperError()

    def post(self, *args, **kwargs):
        raise ForbiddenAsPassiveMapperError()

    def put(self, *args, **kwargs):
        raise ForbiddenAsPassiveMapperError()

    def delete(self, *args, **kwargs):
        raise ForbiddenAsPassiveMapperError()
