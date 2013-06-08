from __future__ import absolute_import, unicode_literals, print_function, division

import base64
import hashlib
import datetime
import re
import sys
import json

from .utilities import _bad_attribute, string
from .client import Client
from .batch import Batch
from .exceptions import APIError, ReadOnlyError


class MailingMeta(type):
    def __getitem__(self, id):
        '''Get the mailing with the specific ID.
                
            Example::

                mailing = stampr.mailing.Mailing[123123]
            
            Args:
                id (int):
                    ID of mailing to retreive.
            
            Returns:
                stampr.mailing.Mailing
        '''
             
        if not isinstance(id, int):
            raise TypeError("id should be a positive int")
        if id <= 0:
            raise ValueError("id should be a positive int")

        mailings = Client.current.get(("mailings", id))

        mailing = mailings[0]
        mailing["return_address"] = mailing["returnaddress"]
        del mailing["returnaddress"]
   
        return Mailing(**mailing)


class Mailing(MailingMeta(str('MailingParent'), (object, ), {})):
    '''An individual piece of mail, within a stampr.batch.Batch

    Args:
        return_address (str):
            Address to return to.
        address (str):
            Address to send to.
        data (str, bytes, Hash):
             Hash for mail merge, str for HTML, bytes for PDF format.
        batch (stampr.batch.Batch):
            Batch to assign this mailing to. If not provided, create a default one.
        mailing_id:
            Internal use only!
        batch_id: 
            Internal use only!
        format:
            Internal use only!
        md5:
            Internal use only!
    '''

    PDF_HEADER_RE = re.compile(b"\\A%PDF")

    STATUSES = ["received", "render", "error", "queued", "assigned", "processing", "printed", "shipped"]
            
    @classmethod
    def browse(cls, start, finish, status=None, batch=None):
        '''Browse mailings

        Get the mailing between two times, optionally only with a specific
        status and/or in a specific batch (batch OR batch_id should be used)
        
        Example::

            start = datetime.datetime(2012, 1, 1, 0, 0, 0)
            end = datetime.now()

            my_batch = stampr.batch.Batch[1234]
        
            mailings = stampr.mailing.Mailing(start, end)
            mailings = stampr.mailing.Mailing(start, end, status="processing")
            mailings = stampr.mailing.Mailing(start, end, batch=my_batch)
            mailings = stampr.mailing.Mailing(start, end, status="processing", batch"my_batch)
        
        Args:
            start (datetime.datetime):
                Start of time period to get mailings for.
            finish (datetime.datetime): 
                End of time period to get mailings for.
            status:
                ["received", "render", "error", "queued", "assigned", "processing", "printed", "shipped"] Status of mailings to find.
            batch (stampr.batch.Batch):
                Batch to retrieve mailings from.
        
        Returns:
            list of stampr.mailing.Mailing
        '''

        if not isinstance(start, datetime.datetime):
            raise TypeError("start should be a datetime.datetime")

        if not isinstance(finish, datetime.datetime):
            raise TypeError("finish should be a datetime.datetime")

        if status is not None:
            if not isinstance(status, string):
                raise TypeError(_bad_attribute(status, cls.STATUSES))

            if status not in cls.STATUSES:
                raise ValueError(_bad_attribute(status, cls.STATUSES))

        if batch is not None:
            if not isinstance(batch, Batch):
                raise TypeError("batch should be a stampr.batch.Batch")

            batch_id = batch.id
        else:
            batch_id = None

        if batch_id is not None and status is not None:
            search = ("batches", batch_id, "with", status)
        elif batch_id is not None:
            search = ("batches", batch_id, "browse")
        elif status is not None:
            search = ("mailings", "with", status)
        else:
            search = ("mailings", "browse")

        search += (start.isoformat(), finish.isoformat())

        all_mailings = []
        i = 0

        while True:
            mailings = Client.current.get(search + (i, ))

            if not mailings:
                break

            all_mailings.extend(mailings)

            i += 1

        # Correct the naming.
        for mailing in all_mailings:
            mailing["return_address"] = mailing["returnaddress"]
            del mailing["returnaddress"]

        return [Mailing(**m) for m in all_mailings]

    
    def is_created(self):
        '''Has the Batch been created already?'''
        return self._id is not None

        
    def __init__(self, return_address=None, address=None, data=None, batch=None, status=None,
                 batch_id=None, mailing_id=None, format=None, md5=None):
        if batch_id is not None and batch is not None:
            raise ValueError("Must supply batch_id OR batch")

        # batch_id is used internally. Shouldn't be used by-user.
        if batch_id is not None:
            if not isinstance(batch_id, int):
                raise TypeError("batch_id must be an int")
            self._batch_id = batch_id

        elif batch is not None:
            if not isinstance(batch, Batch):
                raise TypeError("batch must be an stampr.batch.Batch")
            self._batch_id = batch.id

        else:
            # Create a batch just for this mailing (not accessible outside this object).
            self._batch = Batch()
            self._batch_id = self._batch.id

        self._address = address
        self._return_address = return_address

        # Decode the data if it has been received through a query. Not if the user set it.
        if data is not None and mailing_id is not None:
            if md5 is not None:
                _md5 = hashlib.md5()
                _md5.update(data)
                md5_hash = _md5.hexdigest()

                if md5 != md5_hash:
                    raise ValueError("MD5 digest does not match data")

            if sys.version_info[0] < 3:
                data = bytes(data)
            else:
                data = bytes(data, "ascii")

            self._data = base64.decodestring(data)
        else:
            self._data = data

        self._status = status

        self._id = mailing_id


    @property
    def batch_id(self):
        '''The ID of the Batch associated with the mailing. [int]'''
        return self._batch_id


    @property
    def status(self):
        '''Status of the mailing (None before it is sent).

        Use sync() to update this attribute to the current value.

        Can be one of: None, "received", "render", "error", "queued", "assigned", "processing", "printed" or "shipped"
        '''

        return self._status


    @property
    def address(self):
        '''Address to send mail to [str]'''
        return self._address

    @address.setter
    def address(self, value):
        if self.is_created():
            raise ReadOnlyError("address")

        if value is not None and not isinstance(value, string):
            raise TypeError("address must be a string")

        self._address = value


    @property
    def return_address(self):
        '''Address of sender [str]'''
        return self._return_address

    @return_address.setter
    def return_address(self, value):
        if self.is_created():
            raise ReadOnlyError("return_address")

        if value is not None and not isinstance(value, string):
            raise TypeError("return_address must be a String")

        self._return_address = value


    @property
    def data(self):
        '''PDF data string, HTML document string, or key/values (for mail merge) [bytes, str, dict]'''

        return self._data

    @data.setter
    def data(self, value):
        if self.is_created():
            raise ReadOnlyError("data")

        old_data, self._data = self._data, value
        try:
            self.format # Just read format to check that the format is good.
        except TypeError as ex:
            self._data = old_data
            raise ex

    @property
    def id(self):
        '''Get the id of the mailing. Calling this will mail the mailing first, if required.
    
        Returns:
            [int]
        '''

        if not self.is_created():
            self.mail()

        return self._id

    @property
    def format(self):
        '''Format of the data [str]'''

        data = self.data
        if isinstance(data, dict):
            format = "json"
        elif isinstance(data, bytes) and self.PDF_HEADER_RE.match(data):
            format = "pdf"
        elif isinstance(data, string):
            format = "html"
        elif data is None:
            format = "none"
        else:
            raise TypeError("bad format for data")

        return format


    
    def mail(self):
        '''Mail the mailing on the server.'''

        if self.is_created():
            raise APIError("Already mailed")
        if self.address is None:
            raise APIError("address required before mailing")
        if self.return_address is None:
            raise APIError("return_address required before mailing")

        params = {
                "batch_id": self.batch_id,
                "address": self.address,
                "returnaddress": self.return_address,
                "format": self.format,
        }

        if self.format == "json":
            data = json.dumps(self.data)
        elif self.format in ["html", "pdf"]:
            data = self.data
        else:
            data = None

        if data is not None:
            if not isinstance(data, bytes):
                if sys.version_info[0] < 3:
                    data = bytes(data)
                else:
                    data = bytes(data, "ascii")

            data = base64.encodestring(data)
            params["data"] = data

            md5 = hashlib.md5()
            md5.update(params["data"])
            params["md5"] = md5.hexdigest()

        result = Client.current.post(("mailings", ), **params)
                                                                
        self._id = result["mailing_id"]

        self._status = "received"


    def delete(self):
        '''Delete the mailing on the server.'''

        if not self.is_created():
            raise APIError("can't delete() before create()")

        id, self._id = self._id, None

        Client.current.delete(("mailings", id))

    
    def sync(self):
        '''Update the value of status from the server.'''

        if not self.is_created():
            raise APIError("can't sync() before create()")

        mailing = Client.current.get(("mailings", self.id))
        self._status = mailing["status"]


    def __enter__(self):
        return self

    def __exit__(self, *args):
        if not self.is_created():
            self.mail()