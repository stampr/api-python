Stampr
======

Python wrapper for the Stampr API. Tested with Python 2.7 & 3.3.

:Author: Bil Bas (bil.bas.dev@gmail.com)

:Site: https://github.com/stampr/stampr-api-python

:Stampr: http://stam.pr

:License: MIT


Installation
------------

On the command line::

    $ pip install stampr


Usage
-----


Import and authentication
~~~~~~~~~~~~~~~~~~~~~~~~~

Before using stampr, it must be imported and your account authenticated::

    import stampr

    stampr.authenticate("username", "password")

Sending letters via the simple API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In this case, all mailings will be in individual batches and with default config::

    stampr.mail(my_address, dest_address_1, body1)
    stampr.mail(my_address, dest_address_2, body2)


More complex example
~~~~~~~~~~~~~~~~~~~~

Managing config and grouping mailings into a single batch::

    # Config can be shared by batches.
    config = stampr.config.Config()

    # Batches contain one or more mailings.
    with stampr.batch.Batch(config=config) as b:
        with b.mailing() as m:
            m.address = dest_address_1
            m.return_address = my_address
            m.data = body1

        with b.mailing() as m:
            m.address = dest_address_2
            m.return_address = my_address
            m.data = body2

And without using blocks::

    # Config can be shared by batches.
    config = stampr.config.Config()

    # Batches contain one or more mailings.
    batch = stampr.batch.Batch(config=config)

    mailing1 = stampr.mailing.Mailing(batch=batch)
    mailing1.address = dest_address_1
    mailing1.return_address = my_address
    mailing1.data = data1
    mailing1.mail()

    mailing2 = stampr.mailing.Mailing(batch=batch)
    mailing2.address = dest_address_2
    mailing2.return_address = my_address
    mailing2.data = data2
    mailing2.mail()


Configs
~~~~~~~

Browsing::

    config = stampr.config.Config[123123]
    configs = stampr.config.Config.all()

Configs cannot be deleted.


Batches
~~~~~~~

Browsing::

    import datetime

    batch = stampr.batch.Batch[2451]

    start, end = datetime.datetime(2012, 1, 1, 0, 0, 0), datetime.now()

    batches = stampr.batch.Batch.browse(start, end)
    batches = stampr.batch.Batch.browse(start, end, status="processing")

Updating::

    batch = stampr.batch.Batch[2451]
    batch.status = "archive"

Deletion::

    batch = stampr.batch.Batch[2451]
    batch.delete()


Mailings
~~~~~~~~

Browsing::

    import datetime
    mailing = stampr.mailing.Mailing[123123]

    start, end = datetime.datetime(2012, 1, 1, 0, 0, 0), datetime.now()
    my_batch = stampr.batch.Batch[1234]

    mailings = stampr.mailing.Mailing.browse(start, end)
    mailings = stampr.mailing.Mailing.browse(start, end, status="processing"]
    mailings = stampr.mailing.Mailing.browse(start, end, batch=my_batch]
    mailings = stampr.mailing.Mailing.browse(start, end, status="processing", batch=my_batch]

Syncing current status::

    mailing = stampr.mailing.Mailing[2451]
    mailing.status #=> :received

    # ...later...
    mailing.sync()
    mailing.status #=> :render

Deletion::

    mailing = stampr.mailing.Mailing[2451]
    mailing.delete()


Mail-merge with Mustache templating language
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using Mustache (http://mustache.github.io/)::

    with stampr.batch.Batch() as b:
        b.template = "<html>Hello {{name}}, would you like to buy some {{items}}!</html>"

        with b.mailing() as m:
            m.address = dest_address_1
            m.return_address = my_address
            m.data = { "name": "Marie", "items": "electric eels" }

        with b.mailing() as m:
            m.address = dest_address_2
            m.return_address = my_address
            m.data = { "name": "Romy", "items": "scintillating hackers" }

Building
--------

Additional dependencies::

    $ pip install shovel
    $ pip instlal sphinx

Build documentation with::

    $ shovel docs

Build release package::

    $ shovel release


Contributing
------------

1. Fork it
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create new Pull Request
