Stampr
======

Python wrapper for the Stampr API. Tested with Python 2.7 & 3.3.

Author: Bil Bas (bil.bas.dev@gmail.com)

Site: https://github.com/stampr/stampr-api-python

Stampr: http://stam.pr

License: MIT


Installation
------------

```bash
$ pip install stampr
```

Usage
-----

### Import and authentication

Before using stampr, it must be imported and your account authenticated:

```python
import stampr

stampr.authenticate("username", "password")
```

### Example of sending letters via the simple API

In this case, all mailings will be in individual batches and with default config.

```python
stampr.mail(my_address, dest_address_1, body1)
stampr.mail(my_address, dest_address_2, body2)
```

### More complex example

Managing config and grouping mailings into a single batch.

```python
# Config can be shared by batches.
config = stampr.Config()

# Batches contain one or more mailings.
with stampr.Batch(config=config) as b:
    with b.mailing() as m:
        m.address = dest_address_1
        m.return_address = my_address
        m.data = body1

    with b.mailing() as m:
        m.address = dest_address_2
        m.return_address = my_address
        m.data = body2
```

And without using blocks:

```python
# Config can be shared by batches.
config = stampr.Config()

# Batches contain one or more mailings.
batch = stampr.Batch(config=config)

mailing1 = Mailing(batch=batch)
mailing1.address = dest_address_1
mailing1.return_address = my_address
mailing1.data = data1
mailing1.mail()

mailing2 = Mailing(batch=batch)
mailing2.address = dest_address_2
mailing2.return_address = my_address
mailing2.data = data2
mailing2.mail()
```

### Configs

Browsing: 

```python
config = stampr.Config[123123]
configs = stampr.Config.all()
```

Configs cannot be deleted.

### Batches

Browsing:

```python
import datetime

batch = stampr.Batch[2451]

start, end = datetime.datetime(2012, 1, 1, 0, 0, 0), datetime.now()

batches = stampr.Batch.browse(start, end)
batches = stampr.Batch.browse(start, end, status="processing")
```

Updating:

```python
batch = stampr.Batch[2451]
batch.status = "archive"
```

Deletion:

```python
batch = stampr.Batch[2451]
batch.delete()
```

### Mailings

Browsing:

```python
import datetime
mailing = stampr.Mailing[123123]

start, end = datetime.datetime(2012, 1, 1, 0, 0, 0), datetime.now()
my_batch = stampr.Batch[1234]

mailings = stampr.Mailing.browse(start, end)
mailings = stampr.Mailing.browse(start, end, status="processing"]
mailings = stampr.Mailing.browse(start, end, batch=my_batch]
mailings = stampr.Mailing.browse(start, end, status="processing", batch=my_batch]
```

Syncing current status:

```python
mailing = stampr.Mailing[2451]
mailing.status #=> :received
mailing.sync()
mailing.status #=> :render
```

Deletion:

```python
mailing = stampr.Mailing[2451]
mailing.delete()
```

### Using mail-merge with [Mustache template](http://mustache.github.io/)

```python
with stampr.Batch() as b:
    b.template = "<html>Hello {{name}}, would you like to buy some {{items}}!</html>"

    with b.mailing() as m:
        m.address = dest_address_1
        m.return_address = my_address
        m.data = { "name": "Marie", "items": "electric eels" }

    with b.mailing() as m:
        m.address = dest_address_2
        m.return_address = my_address
        m.data = { "name": "Romy", "items": "scintillating hackers" }
```


Contributing
------------

1. Fork it
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create new Pull Request
