from __future__ import absolute_import, unicode_literals, print_function, division


class Error(Exception):
    '''General error with the Stampr module'''
    pass

class HTTPError(Error):
    '''Problem with the HTTP connection or authentication'''
    def __init__(self, status_code, message):
        self.status_code = status_code
        super(HTTPError, self).__init__(message)


class RequestError(Error):
    '''Bad request to the server.'''
    pass

class APIError(Error):
    '''Problem with interfacing with rules of the API'''
    pass


class ReadOnlyError(Error):
    '''User attempts to alter read-only attribute.'''
    def __init__(self, attribute):
        super(ReadOnlyError, self).__init__("can't modify attribute: #{attribute}")
