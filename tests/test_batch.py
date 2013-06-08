from __future__ import absolute_import, unicode_literals, print_function, division

import sys
import os
import datetime
import json

from pytest import raises
from flexmock import flexmock

from .helper import json_data, json_str

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import stampr

class Test(object):
    def setup(self):
        (flexmock(stampr.client.Client).should_receive("ping").once())
        stampr.authenticate("user", "pass")

        self.created = stampr.batch.Batch(batch_id=2, config_id=1)
        self.uncreated = stampr.batch.Batch(config_id=1)

        self.start = datetime.datetime(1900, 1, 1, 0, 0, 0)
        self.finish = datetime.datetime(2000, 1, 1, 0, 0, 0)


class TestBatchInit(Test):
    def test_generate_a_config(self):
        (flexmock(stampr.client.Client.current)
                .should_receive("_api")
                .with_args("post", ("configs", ),
                           returnenvelope=False,
                           output="single",
                           turnaround="threeday",
                           size="standard",
                           style="color")
                .and_return({ "config_id": 7 }))
        subject = stampr.batch.Batch()
        assert subject.config_id == 7


    def test_failure_with_config_and_config_id(self):
        with raises(ValueError):
            stampr.batch.Batch(config_id=2, config=flexmock())


class TestBatchBlock(Test):
    def test_yield_itself(self):
        yielded = None
        batch = stampr.batch.Batch(config_id=1)
        with batch as b:
            yielded = b

        assert yielded == batch


class TestBatchInitDefault(Test):
    def test_that_it_has_a_config_id(self):
        assert self.uncreated.config_id == 1

    def test_that_it_has_no_template(self):
        assert self.uncreated.template is None

    def test_that_it_has_a_default_status(self):
        assert self.uncreated.status == "processing"



class TestBatchInitFromData(Test):
    def setup(self):
        super(TestBatchInitFromData, self).setup()

        self.created_from_data = stampr.batch.Batch(**json_data("batch_create"))

    def test_that_it_has_a_config_id(self):
        assert self.created_from_data.config_id == 1

    def test_that_it_has_a_template(self):
        assert self.created_from_data.template == "bleh"

    def test_that_it_has_a_status(self):
        assert self.created_from_data.status == "processing"

    def test_that_it_has_an_id(self):
        assert self.created_from_data.id == 2


class TestBatchTemplate(Test):
    def test_set_the_value(self):
        subject = self.uncreated
        subject.template = "hello"
        assert subject.template == "hello"

    def test_accept_none(self):
        subject = self.uncreated
        subject.template = None
        assert subject.template is None

    def test_fail_with_a_bad_type(self):
        with raises(TypeError):
            self.uncreated.template = 12

    def test_fail_if_the_batch_is_already_created(self):
        with raises(stampr.exceptions.ReadOnlyError):
            self.created.template = "hello"


class TestBatchStatusNotCreated(Test):
    def test_accept_a_correct_value(self):
        subject = self.uncreated
        assert subject.status == "processing" # The default.
        subject.status = "hold"
        assert subject.status == "hold"

    def test_refuse_incorrect_string(self):
        with raises(ValueError):
            self.uncreated.status = "frog"

    def test_bad_type(self):
        with raises(TypeError):
            self.uncreated.status = 14


class TestBatchStatusCreated(Test):
    def test_no_authentication(self):
        stampr.client.Client._current = stampr.client.NullClient()
        with raises(stampr.exceptions.APIError):
            self.created.status = "hold"

    def test_accept_a_correct_value_and_update(self):
        subject = self.created

        (flexmock(stampr.client.Client.current)
                .should_receive("_api")
                .with_args("post", ["batches", 2], status="hold")
                .and_return(json_data("batch_create")))

        assert subject.status == "processing"
        subject.status = "hold"
        assert subject.status == "hold"

    def test_do_nothing_if_value_hasnt_changed(self):
        subject = self.created
        subject.status = "processing"
        assert subject.status == "processing"


class TestBatchCreate(Test):
    def test_no_authentication(self):
        stampr.client.Client._current = stampr.client.NullClient()
        with raises(stampr.exceptions.APIError):
            self.uncreated.create()

    def test_post_a_creation_request_without_a_template(self):
        subject = self.uncreated

        (flexmock(stampr.client.Client.current)
                .should_receive("_api")
                .with_args("post", ["batches"], config_id=1, status="processing")
                .and_return(json_data("batch_create")))

        subject.create()
        assert subject.id == 2


    def test_post_a_creation_request_with_a_template(self):
        subject = stampr.batch.Batch(config_id=1, template="Bleh")

        (flexmock(stampr.client.Client.current)
                .should_receive("_api")
                .with_args("post", ["batches"], config_id=1, status="processing", template="Bleh")
                .and_return(json_data("batch_create")))

        subject.create()
        assert subject.id == 2


class TestBatchDelete(Test):
    def test_no_authentication(self):
        stampr.client.Client._current = stampr.client.NullClient()
        with raises(stampr.exceptions.APIError):
            self.created.delete()

    def test_delete_the_batch(self):
        subject = stampr.batch.Batch(config_id=1, template="Bleh", batch_id=2)

        (flexmock(stampr.client.Client.current)
                .should_receive("_api")
                .with_args("delete", ["batches", 2])
                .and_return(True))

        subject.delete()


    def test_fail_if_the_batch_isnt_created_yet(self):
        with raises(stampr.exceptions.APIError):
            self.uncreated.delete()


class TestBatchIndex(Test):
    def test_no_authentication(self):
        stampr.client.Client._current = stampr.client.NullClient()
        with raises(stampr.exceptions.APIError):
            stampr.batch.Batch[4677]

    def test_retreive_a_specific_batch(self):
        (flexmock(stampr.client.Client.current)
                .should_receive("_api")
                .with_args("get", ["batches", 1])
                .and_return(json_data("batch_index")))

        batch = stampr.batch.Batch[1]

        assert batch.id == 2


    def test_fail_with_a_negative_id(self):
        with raises(ValueError):
            stampr.batch.Batch[-1]


    def test_fail_with_a_bad_id(self):
        with raises(TypeError):
            stampr.batch.Batch["fred"]


class TestBatchBrowse(Test):
    def test_no_authentication(self):
        stampr.client.Client._current = stampr.client.NullClient()
        with raises(stampr.exceptions.APIError):
            stampr.batch.Batch.browse(self.start, self.finish)

    def test_retrieve_a_list_over_a_period(self):
        for i in [0, 1, 2]:
            (flexmock(stampr.client.Client.current)
                .should_receive("_api")
                .with_args("get", ("batches", "browse", "1900-01-01T00:00:00", "2000-01-01T00:00:00", i))
                .and_return(json_data("batches_%d" % i)))

        batches = stampr.batch.Batch.browse(self.start, self.finish)

        assert [b.id for b in batches] == [2, 3, 4]

    def test_fail_with_bad_start(self):
        with raises(TypeError):
            stampr.batch.Batch.browse(1, 3)


class TestBatchBrowseWithStatus(Test):
    def test_retrieve_a_list_of_batches_over_a_period_with_given_status(self):
        for i in [0, 1, 2]:
            (flexmock(stampr.client.Client.current)
                .should_receive("_api")
                .with_args("get", ("batches", "with", "processing", "1900-01-01T00:00:00", "2000-01-01T00:00:00", i))
                .and_return(json_data("batches_%d" % i)))

        batches = stampr.batch.Batch.browse(self.start, self.finish, status="processing")

        assert [b.id for b in batches] == [2, 3, 4]

    def test_fail_with_a_bad_status_type(self):
        with raises(TypeError):
            stampr.batch.Batch.browse(self.start, self.finish, status=12)

    def test_fail_with_a_bad_status_value(self):
        with raises(ValueError):
            stampr.batch.Batch.browse(self.start, self.finish, status="frog")

    def test_fail_with_a_bad_period(self):
        with raises(TypeError):
            stampr.batch.Batch.browse(1, 3, status="processing")


class TestBatchMailing(Test):
    def test_create_a_mailing(self):
        (flexmock(stampr.client.Client.current)
                .should_receive("_api")
                .with_args("post", ("configs", ),
                           returnenvelope=False, 
                           output="single",
                           turnaround="threeday",
                           size="standard",
                           style="color")
                .and_return({ "config_id": 7 }))

        batch = stampr.batch.Batch(batch_id=6, template="frog")

        mail = batch.mailing()

        assert isinstance(mail, stampr.mailing.Mailing)
        assert mail.batch_id == 6