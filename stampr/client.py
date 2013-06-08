from __future__ import absolute_import, unicode_literals, print_function, division

import os
import json
import datetime

import requests
import dateutil.parser
import certifi

from .utilities import _bad_attribute, string
from .exceptions import APIError, HTTPError

os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

class NullClient(object):
    '''Client when there is no client specified (that is, the user hasn't authenticated)'''

    @classmethod
    def __getattr__(cls, name):
        raise APIError("Not authenticated! Use stampr.authenticate() first.")


class ClientMeta(type):
    _current = NullClient() # Current client created via authenticate().

    @property
    def current(self):
        return self._current


class Client((ClientMeta(str('ClientParent'), (object, ), {}))):
    '''Client that handles the actual RESTful actions.

    Args:
        username: [string]
        password: [string]
    '''

    BASE_URI = "https://testing.dev.stam.pr/api"
    
    def __init__(self, username, password):
        if not isinstance(username, string):
            raise TypeError("username must be a string")
        if not isinstance(password, string):
            raise TypeError("password must be a string")

        self._username, self._password = username, password
        self.ping()

        Client._current = self


    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    def mail(self, return_address, address, body, config=None, batch=None):
        '''Send a simple HTML or PDF email, in its own batch and default config (unless :batch and/or :config options are used).
        
        Example::

            client = stampr.client.Client("user", "pass")
            client.mail(return_address, address1, "<html><body><p>Hello world!</p></body></html>")
            client.mail(return_address, address2, "<html><body><p>Goodbye world!</p></body></html>")
        
        Args:
            return_address (str):
                Return address.
            address (str):
                Address
            body (str, bytes):
                HTML or PDF data.
            config (stampr.config.Config):
                Config to use for this mailing (or default will be created).
            batch (stampr.batch.Batch):
                Batch to use for this mailing (or default will be created).

        Returns:
            [stampr.mailing.Mailing] The mailing object representing the mail sent.
        '''

        from .config import Config
        from .batch import Batch

        if not isinstance(return_address, string) or not return_address:
            raise TypeError("from must be a non-empty string")
        if not isinstance(address, string) or not address:
            raise TypeError("to must be a non-empty string")
        if not isinstance(address, string):
            raise TypeError("body must be a string")

        if config is None:
            config = Config()
        elif not isinstance(config, Config):
            raise TypeError("config must be a stampr.config.Config")

        if batch is None:
            batch = Batch(config=config)
        elif not isinstance(batch, Batch):
            raise TypeError("batch must be a stampr.batch.Batch")

        with Mailing(batch=batch) as m:
            m.address = address
            m.return_address = return_address
            m.data = body

        return m


    def server_time(self):
        '''Time on the server [datetime.datetime]'''

        result = self.get(("test", "ping"))
        date = dateutil.parser.parse(result["pong"])
        return date


    def ping(self):
        '''Number of seconds to/from server [float]'''

        sent = datetime.datetime.now()
        self.get(("test", "ping"))
        delta = datetime.datetime.now() - sent
        duration = delta.seconds + delta.microseconds / 1000000
        return duration / 2


    def get(self, path):
        '''Send a HTTP GET request.'''

        return self._api("get", path)


    def post(self, path, **params):
        '''Send a HTTP POST request.'''

        return self._api("post", path, **params)


    def delete(self, path):
        '''Send a HTTP DELETE request.'''

        return self._api("delete", path)

    
    def _api(self, action, path, **params):
        '''Actually send a RESTful action to path.'''

        if not isinstance(path, tuple):
            raise TypeError("Expected path to be a tuple")

        path = "/".join(str(dir) for dir in path)

        action_method = getattr(requests, action)
        response = action_method(self.BASE_URI + path, data=params, auth=(self.username, self.password))

        if response.status_code != requests.codes.ok:
            # Wrap the error in one of our own.
            try:
                response.raise_for_status()
            except Exception as ex:
                raise HTTPError(response.status_code, ex)


        return json.loads(response.json())