Python Netbox API
=================

[![Build Status](https://travis-ci.org/Anthony25/python-netboxapi.svg?branch=master)](https://travis-ci.org/Anthony25/python-netboxapi)  [![Coverage Status](https://coveralls.io/repos/github/Anthony25/python-netboxapi/badge.svg?branch=master)](https://coveralls.io/github/Anthony25/python-netboxapi?branch=master)

Python client API for Netbox, using requests.


Usage
-----

Netbox API
==========

Import `NetboxAPI`:

```python
from netboxapi import NetboxAPI
```

Initialize a new `NetboxAPI` object:

```python
netbox_api = NetboxAPI(url="netbox.example.com")

# or if you enabled the authentication
netbox_api = NetboxAPI(
    url="netbox.example.com", username="user", password="password"
)

# or if you have generated a token
netbox_api = NetboxAPI(
    url="netbox.example.com", token="token"
)

# but the following is useless, as the token will not be used
netbox_api = NetboxAPI(
    url="netbox.example.com", username="user", password="password",
    token="token"
)
```

Then use multiple available methods to interact with the api:

```python
>>> netbox_api.get("api/dcim/sites/1/racks")
{
    "id": 1,
    "name": "Some rack",
    …
}
```

Netbox Mapper
=============

`NetboxMapper` is available to interact with Netbox objects. Received json from
the netbox API is converted into mapper objects, by setting its attributes
accordingly to the dict. To use it, first import `NetboxMapper`:

```python
from netboxapi import NetboxAPI, NetboxMapper
```

Initialize a new `NetboxMapper` object:

```python
netbox_api = NetboxAPI(
    url="netbox.example.com", username="user", password="password"
)
netbox_mapper = NetboxMapper(netbox_api, app_name="dcim", model="sites")
```

Then get all objects of the model:

```python
>>> sites = list(netbox_mapper.get())
[<NetboxMapper>, <NetboxMapper>, …]

>>> print(sites[0].id)
1
>>> print(sites[0].name)
"Some site"
```

Or get a specific site by its id:

```python
>>> netbox_mapper.get(1)
```


Dependencies
------------
  * python 3.4 (it certainly works with prior versions, just not tested)


License
-------

Tool under the BSD license. Do not hesitate to report bugs, ask me some
questions or do some pull request if you want to!
