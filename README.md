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
netbox_api = NetboxAPI(url="netbox.example.com/api")

# or if you enabled the authentication
netbox_api = NetboxAPI(
    url="netbox.example.com/api", username="user", password="password"
)

# or if you have generated a token
netbox_api = NetboxAPI(
    url="netbox.example.com/api", token="token"
)

# but the following is useless, as the token will not be used
netbox_api = NetboxAPI(
    url="netbox.example.com/api", username="user", password="password",
    token="token"
)
```

Then use multiple available methods to interact with the api:

```python
>>> netbox_api.get("dcim/sites/1/racks/")
{
    "id": 1,
    "name": "Some rack",
    …
}

>>> netbox_api.post("dcim/device-roles/", json={"name": "test", …},)
{
    "id": 1,
    "name": "test",
    …
}

>>> netbox_api.patch("dcim/device-roles/", json={"slug": "test"},)
{
    "id": 1,
    "name": "test",
    "slug": "test",
    …
}

>>> netbox_api.put("dcim/device-roles/1/", json={"name": "test", …},)
{
    "id": 1,
    "name": "test",
    "slug": "test",
    …
}

>>> netbox_api.delete("dcim/sites/1/")
<<Response [204]>>
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
    url="netbox.example.com/api", username="user", password="password"
)
netbox_mapper = NetboxMapper(netbox_api, app_name="dcim", model="sites")
```

### GET

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

It is possible to get a subresourses of an object, and/or specify a query:

```python
>>> netbox_mapper.get("1", "racks", q="name_to_filter")
```

Any `kwargs` (here `q=`) is used as a GET parameter for the request.

### POST

Use the `kwargs` of a mapper to send a post request and create a new object:

```python
>>> netbox_mapper.post(name="A site", slug="a_site", region="Some region")
<NetboxMapper>  # corresponding to the new created object
```

### PUT

Use `put()` in a child mapper to update the resource upstream by reflecting
the changes made in the object attributes:

```python
>>> child_mapper = netbox_mapper.get(1)
>>> child_mapper.name = "another name"
>>> child_mapper.put()
<NetboxMapper>  # corresponding to the updated object
```

### PATCH

`PATCH` is not supported in mappers, as it does not make really sense (to me)
with the mapper logic.

### DELETE

Delete an object upstream by calling `delete()`:

```python
>>> netbox_mapper.delete(1)
<requests>  # requests object containing the netbox response

# OR

>>> child_mapper = netbox_mapper.get(1)
>>> child_mapper.delete()
<requests>  # requests object containing the netbox response
```

But trying to delete another object of the same model from a child mapper is
not possible:

```python
>>> child_mapper = netbox_mapper.get(1)
>>> child_mapper.delete(2)
Exception ForbiddenAsChildError
```

Dependencies
------------
  * python 3.4 (it certainly works with prior versions, just not tested)


License
-------

Tool under the BSD license. Do not hesitate to report bugs, ask me some
questions or do some pull request if you want to!
