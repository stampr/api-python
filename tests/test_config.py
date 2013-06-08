from __future__ import absolute_import, unicode_literals, print_function, division

import sys
import os
import datetime

from pytest import raises
from flexmock import flexmock

from .helper import json_data, json_str

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import stampr

class Test(object):
    def setup(self):
        (flexmock(stampr.client.Client).should_receive("ping").once())
        stampr.authenticate("user", "pass")

        self.uncreated = stampr.config.Config()
        self.created = stampr.config.Config(config_id=1)
        

class TestConfigDefault(Test):
    def test_default_values(self):
        config = self.uncreated
        assert config.size == "standard"
        assert config.turnaround == "threeday"
        assert config.style == "color"
        assert config.output == "single"
        assert config.return_envelope == False
         

class TestConfigInitFromData(Test):
    def setup(self):
        config = Config(json_data("config_create"))
        assert config.id == 4677
        assert config.size == "standard"
        assert config.turnaround == "threeday"
        assert config.style == "color"
        assert config.output == "single"
        assert config.return_envelope == False


class TestConfigStyle(Test):
    def test_setting(self):
        self.uncreated.style = "color"
        assert self.uncreated.style == "color"

    def test_bad_type(self):
        with raises(TypeError):
            self.uncreated.style = 12

    def test_bad_value(self):
        with raises(ValueError):
            self.uncreated.style = "fish"

    def test_after_create(self):
        with raises(stampr.exceptions.ReadOnlyError):
            self.created.style = "color"


class TestConfigTurnaround(Test):
    def test_setting(self):
        self.uncreated.turnaround = "threeday"
        assert self.uncreated.turnaround == "threeday"

    def test_bad_type(self):
        with raises(TypeError):
            self.uncreated.turnaround = 12

    def test_bad_value(self):
        with raises(ValueError):
            self.uncreated.turnaround = "fish"

    def test_after_create(self):
        with raises(stampr.exceptions.ReadOnlyError):
            self.created.turnaround = "threeday"


class TestConfigOutput(Test):
    def test_setting(self):
        self.uncreated.output = "single"
        assert self.uncreated.output == "single"

    def test_bad_type(self):
        with raises(TypeError):
            self.uncreated.output = 12

    def test_bad_value(self):
        with raises(ValueError):
            self.uncreated.output = "fish"

    def test_after_create(self):
        with raises(stampr.exceptions.ReadOnlyError):
            self.created.output = "single"


class TestConfigSize(Test):
    def test_setting(self):
        self.uncreated.size = "standard"
        assert self.uncreated.size == "standard"

    def test_bad_type(self):
        with raises(TypeError):
            self.uncreated.size = 12

    def test_bad_value(self):
        with raises(ValueError):
            self.uncreated.size = "fish"

    def test_after_create(self):
        with raises(stampr.exceptions.ReadOnlyError):
            self.created.size = "standard"


class TestConfigReturnEnvelope(Test):
    def test_setting(self):
        self.uncreated.return_envelope = False
        assert self.uncreated.return_envelope == False

    def test_bad_type(self):
        with raises(TypeError):
            self.uncreated.return_envelope = 12

    def test_after_create(self):
        with raises(stampr.exceptions.ReadOnlyError):
            self.created.return_envelope = False


class TestConfigCreate(Test):
    def test_no_authentication(self):
        stampr.client.Client._current = stampr.client.NullClient()
        with raises(stampr.exceptions.APIError):
            self.uncreated.create()

    def test_creation(self):
        (flexmock(stampr.client.Client.current)
            .should_receive("_api")
            .with_args("post", ("configs",), output="single", returnenvelope=False, size="standard", style="color", turnaround="threeday")
            .and_return(json_data("config_create")))

        config = self.uncreated
        config.create()
        assert config.id == 4677


class TestConfigIndex(Test):
    def test_no_authentication(self):
        stampr.client.Client._current = stampr.client.NullClient()
        with raises(stampr.exceptions.APIError):
            stampr.config.Config[4677]

    def test_indexing(self):
        (flexmock(stampr.client.Client.current)
            .should_receive("_api")
            .with_args("get", ("configs", 4677))
            .and_return(json_data("config_index")))

        config = stampr.config.Config[4677]

        assert isinstance(config, stampr.config.Config)
        assert config.id == 4677

    def test_bad_type(self):
        with raises(TypeError):
            stampr.config.Config["frog"]

    def test_bad_value(self):
        with raises(ValueError):
            stampr.config.Config[-1]

    def test_not_exists(self):
        (flexmock(stampr.client.Client.current)
            .should_receive("_api")
            .with_args("get", ("configs", 4677))
            .and_return([]))

        with raises(stampr.exceptions.RequestError):
            stampr.config.Config[4677]


class TestConfigAll(Test):
    def test_no_authentication(self):
        stampr.client.Client._current = stampr.client.NullClient()
        with raises(stampr.exceptions.APIError):
            stampr.config.Config.all()

    def test_getting_list(self):
        for i in [0, 1, 2]:
            (flexmock(stampr.client.Client.current)
                .should_receive("_api")
                .with_args("get", ("configs", "browse", "all", i))
                .and_return(json_data("configs_%d" % i)))

        configs = stampr.config.Config.all()
        config_ids = [c.id for c in configs]

        assert all(isinstance(c, stampr.config.Config) for c in configs)
        assert config_ids == [4677, 4678, 4679]
