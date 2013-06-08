from __future__ import absolute_import, unicode_literals, print_function, division

import sys
import os

from pytest import raises
from flexmock import flexmock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import stampr

class TestAuthenticate(object):
    def test_creates_client(self):
        stampr.authenticate("user", "pass")


class TestMail(object):
    def test_no_authentication(self):
        stampr.Client.current = None
        with raises(stampr.APIError):
            stampr.mail("from", "to", "body")

    def test_delegates_to_the_client(self):
        stampr.authenticate("user", "pass")

        new_mailing = flexmock(stampr.Mailing)
        (flexmock(stampr.Client.current)
            .should_receive("mail")
            .with_args("from", "to", "body", None, None)
            .and_return(new_mailing))

        mailing = stampr.mail("from", "to", "body")
        assert mailing == new_mailing