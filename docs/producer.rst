********
Producer
********

.. py:module:: kser.producer

The goal of a producer is to connect onto a Kafka server partition and write into it a serialized :class:`kser.transport.Message`.

.. py:class:: Producer(config)

    Create new Producer instance using provided configuration dict.

    :param dict config: configuration

    .. py:method:: send(topic, kmsg)

        Send the message into the given topic

        :param str topic: a kafka topic
        :param ksr.transport.Message kmsg: Message to serialize
        :return: Execution result
        :rtype: kser.result.Result


.. seealso::

    librdkafka - the Apache Kafka C/C++ client library
        `All configuration variables availables <https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md>`_

    Confluent's Python Client for Apache Kafka
        `Documentation <http://docs.confluent.io/current/clients/confluent-kafka-python/index.html>`_
