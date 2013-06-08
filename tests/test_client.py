from __future__ import absolute_import, unicode_literals, print_function, division

import sys
import os
import datetime

import dateutil

from pytest import raises
from flexmock import flexmock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import stampr

class Test(object):
    def setup(self):
        self.client = stampr.Client("user", "pass")

class TestClientInit(Test):
    def test_creation(self):
       assert self.client.username == "user"
       assert self.client.password == "pass"


class TestClientPing(Test):
    def test_ping_works(self):
        now = "2013-05-16 18:02:47+01:00"

        (flexmock(self.client)
                .should_receive("_api")
                .with_args("get", ("test", "ping"))
                .and_return({ "pong": now }))

        ping = self.client.ping()

        # Todo: Could do this better, but hard to mock datetime.datetime.now()
        assert ping > 0
        assert ping < 0.0001


class TestClientServerTime(Test):
    def test_getting_server_time(self):
        time = datetime.datetime(2013, 5, 16, 18, 2, 47, 0, dateutil.parser.tz.tzutc())

        (flexmock(self.client)
                .should_receive("_api")
                .with_args("get", ("test", "ping"))
                .and_return({ "pong": str(time) }))

        server_time = self.client.server_time()
        assert isinstance(server_time, datetime.datetime)
        assert server_time == time