from __future__ import absolute_import, unicode_literals, print_function, division

from .utilities import _bad_attribute, string
from .client import Client
from .exceptions import ReadOnlyError

class ConfigMeta(type):
    def __getitem__(self, id):
        '''Get the config with a specific id.

        Example::

            config = stampr.config.Config[123123]

        Returns:
            stampr.config.Config
        '''

        if not isinstance(id, int):
            raise TypeError("id must be a positive int")
        elif id <= 0:
            raise ValueError("id must be a positive int")

        configs = Client.current.get(("configs", id))
        config = configs[0]

        # Rename returnenvelope as return_envelope
        config["return_envelope"] = config["returnenvelope"]
        del config["returnenvelope"]

        return self(**config)


class Config(ConfigMeta(str('ConfigParent'), (object, ), {})):
    '''Mailing configuration to be used with Batches

    Args:
        size (str):
            ["standard"]
        turnaround (str):
            ["threeday"]
        style (str):
            ["color"]
        output (str):
            ["single"]
        return_envelope (boolean):
            [False]
        config_id: 
            For internal use only!
        user_id:
            For internal use only!
    '''

    SIZES = ["standard"]
    TURNAROUNDS = ["threeday"]
    STYLES = ["color"]
    OUTPUTS = ["single"]
    RETURN_ENVELOPES = [True, False]


    @classmethod
    def all(cls):
        '''Get a list of all configs defined in your Stampr account.
        
        Example::

            configs = stampr.config.Config.all
        
        Returns:
            list of stampr.config.Config
        '''

        all_configs = []
        i = 0

        while True:
            configs = Client.current.get(("configs", "all", i))
            if not configs:
                break

            all_configs.extend(configs)

            i += 1

        # Rename returnenvelope as return_envelope
        for config in all_configs:
            config["return_envelope"] = config["returnenvelope"]
            del config["returnenvelope"]

        return [Config(**c) for c in all_configs]

    def is_created(self):
        '''Has the Config been created already?'''

        return self._id is not None

    
    def __init__(self,
                 size="standard",
                 turnaround="threeday",
                 style="color",
                 output="single",
                 return_envelope=False,
                 config_id=None,
                 user_id=None):

        self._size = size
        self._turnaround = turnaround
        self._style = style
        self._output = output
        # :returnenvelope is from json, return_envelope is more ruby-frily for-users.
        self._return_envelope = return_envelope

        self._id = config_id


    @property
    def size(self):
        '''The ID of the config associated with the mailing. ["standard"]'''

        return self._size

    @size.setter
    def size(self, value):
        if self.is_created():
            raise ReadOnlyError("size")
        if not isinstance(value, string):
            raise TypeError(_bad_attribute("size", self.SIZES))
        if value not in self.SIZES:
            raise ValueError(_bad_attribute("size", self.SIZES))

        self._size = value


    @property
    def turnaround(self):
        '''Time for turnaround of post ["threeday"]'''

        return self._turnaround

    @turnaround.setter
    def turnaround(self, value):
        if self.is_created():
            raise ReadOnlyError("turnaround")
        if not isinstance(value, string):
            raise TypeError(_bad_attribute("turnaround", self.TURNAROUNDS))
        if value not in self.TURNAROUNDS:
            raise ValueError(_bad_attribute("turnaround", self.TURNAROUNDS))

        self._turnaround = value


    @property
    def style(self):
        '''Style of printing ["color"]'''

        return self._style

    @style.setter
    def style(self, value):
        if self.is_created():
            raise ReadOnlyError("style")
        if not isinstance(value, string):
            raise TypeError(_bad_attribute("style", self.STYLES))
        if value not in self.STYLES:
            raise ValueError(_bad_attribute("style", self.STYLES))

        self._style = value


    @property
    def output(self):
        '''Type of output printing. ["single"]'''

        return self._output

    @output.setter
    def output(self, value):
        if self.is_created():
            raise ReadOnlyError("output")
        if not isinstance(value, string):
            raise TypeError(_bad_attribute("output", self.OUTPUTS))
        if value not in self.OUTPUTS:
            raise ValueError(_bad_attribute("output", self.OUTPUTS))

        self._output = value


    @property
    def return_envelope(self):
        '''Whether to include a return envelop [False]'''

        return self._return_envelope

    @return_envelope.setter
    def return_envelope(self, value):
        if self.is_created():
            raise ReadOnlyError("return_envelope")
        if value not in self.RETURN_ENVELOPES:
            raise TypeError(_bad_attribute("return_envelope", self.RETURN_ENVELOPES))

        self._return_envelope = value


    @property
    def id(self):
        '''Get the id of the configuration. Calling this will create the config first, if required. [int]'''

        if not self.is_created():
            self.create()
        return self._id


    def create(self):
        '''Create the config on the server.'''

        if self.is_created():
            return # Don't re-create if it already exists.

        result = Client.current.post(("configs",),
                                    size=self.size,
                                    turnaround=self.turnaround,
                                    style=self.style,
                                    output=self.output,
                                    returnenvelope=self.return_envelope)

        self._id = result["config_id"]