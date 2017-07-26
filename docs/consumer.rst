********
Consumer
********

.. py:module:: kser.consumer

The goal of a consumer is to connect onto a Kafka server and read partition's records to send them to the :class:`kser.controller.Controller`.

.. py:class:: Consumer(config, topics)

    Create new Consumer instance using provided configuration dict.

    :param dict config: configuration
    :param list(str) topics: Topics to consume

    .. py:attribute:: REGISTRY

        The consumer's registry. The default registry factory is :class:`kser.controller.Controller`, you may override it according to your needs.

    .. py:method:: run()

        The consumer loop to consume Kafka's messages.

.. seealso::

    librdkafka - the Apache Kafka C/C++ client library
        `All configuration variables availables <https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md>`_

    Confluent's Python Client for Apache Kafka
        `Documentation <http://docs.confluent.io/current/clients/confluent-kafka-python/index.html>`_
