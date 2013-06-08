from __future__ import absolute_import, unicode_literals, print_function, division

import sys
import hashlib
import os
import base64
import json
import datetime

import dateutil

from pytest import raises
from flexmock import flexmock

from .helper import json_data, json_str, to_bytes

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import stampr

class Test(object):
    def setup(self):
        (flexmock(stampr.client.Client).should_receive("ping").once())

        stampr.authenticate("user", "pass")

        self.uncreated = stampr.mailing.Mailing(batch_id=1)
        self.created = stampr.mailing.Mailing(mailing_id=2, batch_id=1)
        self.batch = stampr.batch.Batch(batch_id=99, config_id=12)
        self.start = datetime.datetime(1900, 1, 1, 0, 0, 0)
        self.finish = datetime.datetime(2000, 1, 1, 0, 0, 0)


def TestMailingInit(Test):
    def test_generate_batch(self):
        (flexmock(stampr.client.Client.current)
                .should_receive("_api")
                .with_args("post", ["configs"], returnenvelope=False, output="single", turnaround="threeday", size="standard", style="color")
                .and_return({ "config_id": 7 }))

        (flexmock(stampr.client.Client.current)
                .should_receive("_api")
                .with_args("post", ["batches"], config_id=7, status="processing")
                .and_return({ "batch_id": 2 }))

        subject = stampr.mailing.Mailing()
        assert subject.batch_id == 2

    def test_use_both_batch_and_batch_id(self):
        with raises(ValueError):
            stampr.mailing.Mailing(batch_id=2, batch=flexmock())

    def test_bad_data(self):
        with raises(TypeError):
            stampr.mailing.Mailing(batch_id=2, data=12)

    def test_good_md5(self):
        data = "sdfsdf"
        md5 = hashlib.md5()
        md5.update("sdfsdf")
        md5_hash = md5.hexdigest()
        stampr.mailing.Mailing(batch_id=2, mailing_id=12, data="sdf", md5=md5_hash)

    def test_bad_md5(self):
        with raises(ValueError):
            stampr.mailing.Mailing(batch_id=2, mailing_id=12, data="sdf", md5="234234")


class TestMailingMail(Test):
    def test_no_authentication(self):
        stampr.client.Client._current = stampr.client.NullClient()
        with raises(stampr.exceptions.APIError):
            self.uncreated.mail()


    def test_without_data(self):
        subject = stampr.mailing.Mailing(batch_id=2, address="bleh1", return_address="bleh2")

        (flexmock(stampr.client.Client.current)
                .should_receive("_api")
                .with_args("post", ("mailings", ),
                           batch_id=2,
                           address="bleh1", 
                           returnaddress="bleh2",
                           format="none")
                .and_return(json_data("mailing_create")))

        assert subject.status is None
        subject.mail()
        assert subject.id == 1
        assert subject.status == "received"


    def test_with_json_data(self):
        data = { "fred": "savage" }
        encoded = base64.encodestring(to_bytes(json.dumps(data)))

        subject = stampr.mailing.Mailing(batch_id=2, address="bleh1", return_address="bleh2", data=data)

        (flexmock(stampr.client.Client.current)
                .should_receive("_api")
                .with_args("post", ("mailings",),
                           batch_id=2,
                           address="bleh1", 
                           returnaddress="bleh2",
                           format="json",
                           md5="73d5225731ed56a90677df696f889f7f",
                           data=encoded)
                .and_return(json_data("mailing_create")))

        assert subject.status is None
        subject.mail()
        assert subject.id == 1
        assert subject.status == "received"


    def test_with_html_data(self):
        data = "<html>Hello world!</html>"
        encoded = base64.encodestring(to_bytes(data))

        subject = stampr.mailing.Mailing(batch_id=2, address="bleh1", return_address="bleh2", data=data)

        (flexmock(stampr.client.Client.current)
                .should_receive("_api")
                .with_args("post", ("mailings",),
                           batch_id=2,
                           address="bleh1", 
                           returnaddress="bleh2",
                           format="html",
                           md5="4e93ef6f0ebfd2887752065b17ddd3e2",
                           data=encoded)
                .and_return(json_data("mailing_create")))

        assert subject.status is None
        subject.mail()
        assert subject.id == 1
        assert subject.status == "received"


    def test_with_pdf_data(self):
        data = b"%PDF1.4..."
        encoded = base64.encodestring(data)

        subject = stampr.mailing.Mailing(batch_id=2, address="bleh1", return_address="bleh2", data=data)

        (flexmock(stampr.client.Client.current)
                .should_receive("_api")
                .with_args("post", ("mailings",),
                           batch_id=2,
                           address="bleh1", 
                           returnaddress="bleh2",
                           format="pdf",
                           md5="c40b92002dfdac9ee80136d9cc443a2e",
                           data=encoded)
                .and_return(json_data("mailing_create")))

        assert subject.status is None
        subject.mail()
        assert subject.id == 1
        assert subject.status == "received"


    def test_without_an_address(self):
        data = "%PDF1.4..."
        subject = stampr.mailing.Mailing(batch_id=2, return_address="bleh")

        with raises(stampr.exceptions.APIError):
            subject.mail() 

    def test_without_return_address(self):
        data = "%PDF1.4..."
        subject = stampr.mailing.Mailing(batch_id=2, address="bleh")
        with raises(stampr.exceptions.APIError):
            subject.mail()


class TestMailingDelete(Test):
    def test_no_authentication(self):
        stampr.client.Client._current = stampr.client.NullClient()
        with raises(stampr.exceptions.APIError):
            self.created.delete()


    def test_if_created(self):
        data = json_data("mailing_create")
        data["return_address"] = data["returnaddress"]
        del data["returnaddress"]

        subject = stampr.mailing.Mailing(**data)

        (flexmock(stampr.client.Client.current)
                .should_receive("_api")
                .with_args("delete", ("mailings", 1))
                .and_return(json_data("mailing_create")))

        subject.delete()
        assert subject.is_created() == False

    def test_if_isnt_created(self):
        with raises(stampr.exceptions.APIError):
            self.uncreated.delete()


class TestMailingAddress(Test):
    def test_set_value(self):
        self.uncreated.address = "hello"
        assert self.uncreated.address == "hello"

    def test_unset(self):
        self.uncreated.address = None
        assert self.uncreated.address == None

    def test_bad_type(self):
        with raises(TypeError):
            self.uncreated.address = 12 

    def test_alread_created(self):
        with raises(stampr.exceptions.ReadOnlyError):
            self.created.address = "hello"


class TestMailingReturnAddress(Test):
    def test_set_value(self):
        self.uncreated.return_address = "hello"
        assert self.uncreated.return_address == "hello"

    def test_unset(self):
        self.uncreated.return_address = None
        assert self.uncreated.return_address == None

    def test_bad_type(self):
        with raises(TypeError):
            self.uncreated.return_address = 12 

    def test_alread_created(self):
        with raises(stampr.exceptions.ReadOnlyError):
            self.created.return_address = "hello"


class TestMailingData(Test):
    def test_set_value(self):
        self.uncreated.data = "hello"
        assert self.uncreated.data == "hello"

    def test_unset(self):
        self.uncreated.data = None
        assert self.uncreated.data == None

    def test_bad_type(self):
        with raises(TypeError):
            self.uncreated.data = 12 

    def test_alread_created(self):
        with raises(stampr.exceptions.ReadOnlyError):
            self.created.data = "hello"


class TestMailingSync(Test):
    def test_no_authentication(self):
        stampr.client.Client._current = stampr.client.NullClient()
        with raises(stampr.exceptions.APIError):
            self.created.sync()

    def test_if_created(self):
        data = json_data("mailing_create")
        data['status'] = 'render'

        (flexmock(stampr.client.Client.current)
                .should_receive("_api")
                .with_args("get", ("mailings", 2))
                .and_return(data))

        self.created._status = "received"
        assert self.created.status == "received"
        self.created.sync()
        assert self.created.status == "render"

    def test_if_not_created(self):
        with raises(stampr.exceptions.APIError):
            self.uncreated.sync()

class TestMailingIndexing(Test):
    def test_no_authentication(self):
        stampr.client.Client._current = stampr.client.NullClient()
        with raises(stampr.exceptions.APIError):
            stampr.mailing.Mailing[1]

    def test_valid(self):
        (flexmock(stampr.client.Client.current)
                .should_receive("_api")
                .with_args("get", ("mailings", 1))
                .and_return(json_data("mailing_index")))

        mailing = stampr.mailing.Mailing[1]

        assert mailing.id == 1
        assert mailing.status == "received"

    def test_bad_id(self):
        with raises(ValueError):
            stampr.mailing.Mailing[0] 

    def test_bad_type(self):
        with raises(TypeError):
            stampr.mailing.Mailing["fred"]

    def test_valid(self):
        (flexmock(stampr.client.Client.current)
                .should_receive("_api")
                .with_args("get", ("mailings", 1))
                .and_return([]))

        with raises(stampr.exceptions.RequestError):
            stampr.mailing.Mailing[1]
            

class TestMailingBrowse(Test):
    def test_no_authentication(self):
        stampr.client.Client._current = stampr.client.NullClient()
        with raises(stampr.exceptions.APIError):
            stampr.mailing.Mailing.browse(self.start, self.finish)

    def test(self):
        for i in [0, 1, 2]:
            (flexmock(stampr.client.Client.current)
                .should_receive("_api")
                .with_args("get", ("mailings", "browse", "1900-01-01T00:00:00", "2000-01-01T00:00:00", i))
                .and_return(json_data("mailings_%d" % i)))


        mailings = stampr.mailing.Mailing.browse(self.start, self.finish)

        for mailing in mailings:
            assert isinstance(mailing,stampr.mailing.Mailing)

        mailing_ids = [m.id for m in mailings]
        assert mailing_ids == [1, 2, 3]

    def test_with_bad_start(self):
        with raises(TypeError):
            stampr.mailing.Mailing.browse(1, self.finish) 

    def test_with_bad_finish(self):
        with raises(TypeError):
            stampr.mailing.Mailing.browse(self.start, 2)


class TestMailingWithBatch(Test):
    def test(self):
        for i in [0, 1, 2]:
            (flexmock(stampr.client.Client.current)
                .should_receive("_api")
                .with_args("get", ("batches", self.batch.id, "browse", "1900-01-01T00:00:00", "2000-01-01T00:00:00", i))
                .and_return(json_data("mailings_%d" % i)))

        mailings = stampr.mailing.Mailing.browse(self.start, self.finish, batch=self.batch)

        for mailing in mailings:
            assert isinstance(mailing, stampr.mailing.Mailing)

        mailing_ids = [m.id for m in mailings]
        assert mailing_ids == [1, 2, 3]


    def test_bad_batch(self):
        with raises(TypeError):
            stampr.mailing.Mailing.browse(self.start, self.finish, batch=1)


class TestMailingWithStatus(Test):
    def test(self):
        for i in [0, 1, 2]:
            (flexmock(stampr.client.Client.current)
                .should_receive("_api")
                .with_args("get", ("mailings", "with", "processing", "1900-01-01T00:00:00", "2000-01-01T00:00:00", i))
                .and_return(json_data("mailings_%d" % i)))

        mailings = stampr.mailing.Mailing.browse(self.start, self.finish, status="processing")

        for mailing in mailings:
            assert isinstance(mailing, stampr.mailing.Mailing)

        mailing_ids = [m.id for m in mailings]
        assert mailing_ids == [1, 2, 3]

    def test_bad_status_type(self):
        with raises(TypeError):
            stampr.mailing.Mailing.browse(self.start, self.finish, status=12)

    def test_bad_status_value(self):
        with raises(ValueError):
            stampr.mailing.Mailing.browse(self.start, self.finish, status="fish")


class TestMailingWithStatusAndBatch(Test):
    def test(self):
        for i in [0, 1, 2]:
            (flexmock(stampr.client.Client.current)
                .should_receive("_api")
                .with_args("get", ("batches", self.batch.id, "with", "processing", "1900-01-01T00:00:00", "2000-01-01T00:00:00", i))
                .and_return(json_data("mailings_%d" % i)))


        mailings = stampr.mailing.Mailing.browse(self.start, self.finish, status="processing", batch=self.batch)

        for mailing in mailings:
            assert isinstance(mailing, stampr.mailing.Mailing)

        mailing_ids = [m.id for m in mailings]
        assert mailing_ids == [1, 2, 3]


    def test_bad_status_type(self):
        with raises(TypeError):
            stampr.mailing.Mailing.browse(self.start, self.finish, status=12, batch=self.batch)


    def test_bad_status_value(self):
        with raises(ValueError):
            stampr.mailing.Mailing.browse(self.start, self.finish, status="fish", batch=self.batch)


    def test_bad_batch(self):
        with raises(TypeError):
            stampr.mailing.Mailing.browse(self.start, self.finish, status="processing", batch=1)
