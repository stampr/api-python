Stampr
======

Wrapper for the Stampr API.

Author: Bil Bas (bil.bas.dev@gmail.com)

Site: https://github.com/stampr/stampr-api-python

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

### Browsing configs

```python
config = stampr.Config[123123]
configs = stampr.Config.all()
```

### Browsing batches

```python
import datetime

batch = stampr.Batch[2451]

from, to = datetime.datetime(2012, 1, 1, 0, 0, 0), datetime.datetime.today()

batches = stampr.Batch.browse(from, to)
batches = stampr.Batch.browse(from, to, status=stampr.Batch.PROCESSING)
```

### Updating batches

```python
batch = stampr.Batch[2451]
batch.status = stampr.Batch.ARCHIVE
```

### Deleting batches

```python
stampr.Batch[2451].delete()
```

### Browsing mailings

```python
import datetime
mailing = stampr.Mailing[123123]

from, to = datetime.datetime(2012, 1, 1, 0, 0, 0), datetime.datetime.today()
my_batch = stampr.Batch[1234]

mailings = stampr.Mailing.browse(from, to)
mailings = stampr.Mailing.browse(from, to, status=stampr.Mailing.PROCESSING]
mailings = stampr.Mailing.browse(from, to, batch=my_batch]
mailings = stampr.Mailing.browse(from, to, status=stampr.Mailing.PROCESSING, batch=my_batch]
```

### Deleting mailings

```python
stampr.Mailing[2451].delete()
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
