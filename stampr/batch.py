from __future__ import absolute_import, unicode_literals, print_function, division

import datetime

from .utilities import _bad_attribute, string
from .client import Client
from .config import Config
from .exceptions import APIError, ReadOnlyError

class BatchMeta(type):
    def __getitem__(self, id):
        '''Get the batch with the specific ID.
            
            Example::

                batch = stampr.batch.Batch[2451]

            Args:
                id (int):
                    ID of batch to retreive.

            Returns: 
                stampr.batch.Batch
        '''

        if not isinstance(id, int):
            raise TypeError("id should be a positive int")
        elif id < 0:
            raise ValueError("id should be a positive int")

        batches = Client.current.get(["batches", id])

        return self(**batches[0])

class Batch(BatchMeta(str('BatchParent'), (object, ), {})):
    '''A batch of stampr.mailing.Mailing objects

    If neither config_id or config are provided, then a new, default, config will be applied to this batch.
    
    Args:
        config (stampr.config.Config):
            Config to use.
        template (str):
            Mail-merge template (optional)
        status (str):
            ["processing", "hold", "archive"] The initial status of the mailing ("processing")
        config_id:
            For internal use only!
        batch_id:
            For internal use only!
    '''

    __metaclass__ = BatchMeta

    STATUSES = ["processing", "hold", "archive"]  

    @classmethod
    def browse(cls, start, finish, status=None):
        '''Get the batches between two times.
            
        Example::

            start, finish = datetime.datetime(2012, 1, 1, 0, 0, 0), datetime.now()
            batches = stampr.batch.Batch.browse(start, finish)
            batches = stampr.batch.Batch.browse(start, finish, status="processing")
        
        Args:
            start (datetime.datetime):
                Start of time period to get batches for.
            finish (datetime.datetime):
                End of time period to get batches for.
            status (str):
                ["processing", "hold", "archive"] Status of batch to find.
        
        Returns:
            list of stampr.batch.Batch
        '''
        
        if not isinstance(start, datetime.datetime):
            raise TypeError("start should be a datetime.datetime")

        if not isinstance(finish, datetime.datetime):
            raise TypeError("finish should be a datetime.datetime")

        if status is not None:
            if not isinstance(status, string):
                raise TypeError(_bad_attribute(status, cls.STATUSES))
            if not status in cls.STATUSES:
                raise ValueError(_bad_attribute(status, cls.STATUSES))

            search = ("with", status)
        else:
            search = ("browse", )

        all_batches = []
        i = 0

        while True:
            batches = Client.current.get(("batches", ) + search + (start.isoformat(), finish.isoformat(), i))

            if not batches:
                break

            all_batches.extend(batches)

            i += 1

        return [Batch(**b) for b in all_batches]


    # Has the Batch been created already?
    def is_created(self):
        return self._id is not None


    def __init__(self, config=None, template=None, status="processing", config_id=None, batch_id=None,):
        if config is not None and config_id is not None:
            raise ValueError("Must supply config_id OR config")

        elif config_id is not None:
            # Config ID is only used internally. User should use config.
            if not isinstance(config_id, int):
                raise TypeError("config_id must be an int")
            config_id = config_id

        elif config is not None:
            if not isinstance(config, Config):
                raise TypeError("config must be a stampr.config.Config")
            config_id = config.id

        else:
            config = Config()
            config_id = config.id

        self._config_id = config_id
        self._template = template
        self._status = status

        self._id = batch_id or None


    @property
    def config_id(self):
        '''The ID of the config associated with the Batch [int]'''

        return self._config_id


    @property
    def template(self):
        '''Template string, for mail merge, if any. [str, None]'''

        return self._template

    @template.setter
    def template(self, value):
        if self.is_created():
            raise ReadOnlyError("template")

        if value is not None and not isinstance(value, string):
            raise TypeError("template must be a String" )

        self._template = value


    @property
    def status(self):
        '''Status of the mailings in the Batch. ["processing", "hold", "archive"]'''
        return self._status

    @status.setter
    def status(self, value):
        if not isinstance(value, string):
            raise TypeError(_bad_attribute("status", self.STATUSES))
        if not value in self.STATUSES:
            raise ValueError(_bad_attribute("status", self.STATUSES))

        # If we have already been created, update the status.
        if self.is_created() and value is not None and self._status != value:
            params = {
                    "status": value,
            }

            Client.current.post(["batches", self.id], **params)

        self._status = value


    @property
    def id(self):
        '''Get the id of the batch. Calling this will create the batch first, if required.
    
        Returns:
            int
        '''

        if not self.is_created():
            self.create

        return self._id


    
    def create(self):
        '''Create the config on the server.

        Returns: 
            stampr.config.Config
        '''

        if self.is_created(): # Don't re-create if it already exists.
            return

        params = {
                "config_id": self.config_id,
                "status": self.status,
        }

        if self.template is not None:
            params["template"] = self.template 

        result = Client.current.post(["batches"], **params)
                                                                
        self._id = result["batch_id"]

    
    def delete(self):
        '''Delete the config on the server (this will fail if there are mailings still inside the batch).'''

        if not self.is_created():
            raise APIError("Can't delete() before create()")

        id, self._id = self._id, None

        Client.current.delete(["batches", id])


    def mailing(self):
        '''Create a Mailing for this Batch.
    
        Returns:
            stampr.mailing.Mailing
        '''

        from .mailing import Mailing # Avoid circular rependency.

        return Mailing(batch=self)


    def __enter__(self):
        return self


    def __exit__(self, *args):
        pass