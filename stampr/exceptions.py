from __future__ import absolute_import, unicode_literals, print_function, division


# General error with the Stampr module.
class Error(Exception):
    pass

# Problem with the HTTP connection or authentication.
class HTTPError(Error):
    def __init__(self, status_code, message):
        self.status_code = status_code
        super(HTTPError, self).__init__(message)

# Bad request to the server.
class RequestError(Error):
    pass

# Problem with interfacing with rules of the API.
class APIError(Error):
    pass

# User attempts to alter read-only attribute.
class ReadOnlyError(Error):
    def __init__(self, attribute):
        super(ReadOnlyError, self).__init__("can't modify attribute: #{attribute}")
