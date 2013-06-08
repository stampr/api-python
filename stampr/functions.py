from __future__ import absolute_import, unicode_literals, print_function, division

from .client import Client
from .mailing import Mailing
from .exceptions import APIError


def authenticate(username, password):
    '''Authenticate your Stampr account with username and password.

    Args:
        username
            [str] Account username.
        password
            [str] Account password.

    Return
        [stampr.Client]
    '''

    Client.current = Client(username, password)


def mail(return_address, address, body, config=None, batch=None):
    '''Send a simple HTML or PDF email, in its own batch and default config (unless :batch and/or :config options are used).

    Example
        stampr.authenticate("user", "pass")
        stampr.mail(return_address, address1, "<html><body><p>Hello world!</p></body></html>")
        stampr.mail(return_address, address2, "<html><body><p>Goodbye world!</p></body></html>")

    Args:
        return_address
            [str] Return address.
        address
            [str] Address
        body
            [str, bytes] HTML or PDF data.
        config
            [stampr.Config] Config to use (default config will be created if not specified)
        batch
            [stampr.Batch] Batch to add the mailing to (new batch will be created if not specified)

    Return:
        [stampr.Mailing] The mailing object representing the mail sent.
    '''

    if Client.current is None:
        raise APIError("Required to authenticate() before mailing")

    return Client.current.mail(return_address, address, body, config, batch)

