
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
        url = self._url + "/".join(str(a) for a in args)

        return self.netbox_api.get(url, data=kwargs)
