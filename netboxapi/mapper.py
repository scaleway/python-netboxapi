
from .api import NetboxAPI


class NetboxMapper():
    def __init__(self, netbox_api, app_name, model, url=None):
        self.netbox_api = netbox_api
        self.app_name = app_name
        self.model = model

        self._url = (
            url or self.netbox_api.build_model_url(self.app_name, self.model)
        )

    def get(self, *args, **kwargs):
        """
        Get netbox objects

        Use args and kwargs as filters: all *args items are joined with "/",
        and kwargs are use as data parameter. It is then used to build the
        request uri

        Examples:
            >>> netbox_mapper.app_name = "dcim"
            >>> netbox_mapper.model = "sites"
            >>> netbox_mapper.get("1", "racks", q="name_to_filter")

            Will do a request to "/api/dcim/sites/1/racks/?q=name_to_filter"
        """
        url = self._url + "/".join(str(a) for a in args)

        new_mappers_dict = self.netbox_api.get(url, data=kwargs)
        if isinstance(new_mappers_dict, dict):
            new_mappers_dict = [new_mappers_dict]
        for d in new_mappers_dict:
            yield self._build_new_mapper_from(d, url)

    def _build_new_mapper_from(self, mapper_attributes, new_url):
        mapper = type(self)(
            self.netbox_api, self.app_name, self.model, new_url
        )
        for attr, val in mapper_attributes.items():
            setattr(mapper, attr, val)

        return mapper
