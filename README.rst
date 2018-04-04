.. image:: https://img.shields.io/pypi/v/kser.svg
   :target: https://pypi.python.org/pypi/kser/
   :alt: Latest Version

.. image:: https://travis-ci.org/cdumay/kser.svg?branch=master
   :target: https://travis-ci.org/cdumay/kser
   :alt: Latest version


.. image:: https://readthedocs.org/projects/kser/badge/?version=latest
   :target: http://kser.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
    :target: https://github.com/cdumay/kser/blob/master/LICENSE

==============================
Kafka serialize python library
==============================

Kser is a bundle of python library whose purpose is to serialize tasks to be
executed on Kafka consumers. It supports farious extensions:

Transport
=========

librdkafka
----------

You can choose to use the C bindings using `confluent-kafka <https://github.com/confluentinc/confluent-kafka-python>`_:

    $ pip install kser[confluent]

.. note::

    You need to install manually librdkafka, see `confluent-kafka-python documentation <http://docs.confluent.io/current/clients/confluent-kafka-python>`_

kafka-python
------------

You can choose the pure python library `kafka-python <https://github.com/dpkp/kafka-python>`_:

    $ pip install kser[pykafka]

http
----

There is also a light version using HTTP ideal to produce messages (not recommended for consumption)

    $ pip install kser[http]

Other
=====

encrypt data
------------

It is possible to encrypt messages in the Kafka queue using `libsodium <https://github.com/jedisct1/libsodium>`_.

    $ pip install kser[crypto]

.. note::

    You need to install manually libsodium, see `libsodium documentation <https://download.libsodium.org/doc/>`_

Add-ons
=======

- `Flask extension <https://github.com/cdumay/flask-kser>`_: Flask integration.

Requirements
============

- Python 3.x

Documentations
==============

- Project: http://kser.readthedocs.io/
- Libsodium: https://download.libsodium.org/doc/
- confluent-kafka-python: http://docs.confluent.io/current/clients/confluent-kafka-python
- kafka-python: http://kafka-python.readthedocs.io/en/master/

Other links
===========

- PyPI: https://pypi.python.org/pypi/kser
- Project issues: https://github.com/cdumay/kser/issues

License
=======

MIT license