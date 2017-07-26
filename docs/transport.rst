******************
Transport envelops
******************

.. py:module:: kser.transport

A set of Marshmallow schemas to serialize and deserialize data to Kafka server.

.. py:class:: Message(uuid, entrypoint, params=None, result=None, route=None)

    Contains fields used by the :class:`kser.controller.Controller` to route data.

    :param str uuid: It's the message unique key. By default, is a UUID in string format.
    :param str entrypoint: A key used to register an :class:`kser.entry.Entrypoint` into the :class:`kser.controller.Controller`.
    :param dict params: The entrypoint's parameters (Can see it as `**kwargs`)
    :param kser.result.Result result: A previous result.
    :param kser.transport.Route route: Routing metadata.

    .. py:attribute:: MARSHMALLOW_SCHEMA

        A marshmallow Schema instance used to load and dump messages from Kafka's raw text.

    .. py:method:: dump()

        Dump the message as `dict`

    .. py:method:: dumps()

        Dump the message as JSON.

    .. py:method:: loads(json_data)

        Read raw data received from the :class:`kser.consumer.Consumer`.

        :param bytes json_data: Kafka entry.

.. py:class:: Route(uuid, entrypoint, params=None, onerror=None)

    Similar to :class:`Message`, but this class is used to route :class:`kser.entry.Entrypoint` result.

    :param str uuid: It's the message unique key. By default, is a UUID in string format.
    :param str entrypoint: A key used to register an :class:`kser.entry.Entrypoint` into a :class:`kser.controller.Controller`.
    :param dict params: The entrypoint's parameters (Can see it as `**kwargs`)
    :param str onerror: Entrypoint to call on error, if not set `entrypoint` will be used.

    .. py:attribute:: MARSHMALLOW_SCHEMA

        A marshmallow Schema instance used to load and dump messages from Kafka's raw text.

    .. py:method:: dump()

        Dump the message as `dict`

    .. py:method:: dumps()

        Dump the message as JSON.

.. seealso::

    Marshmallow: simplified object serialization
        `Declaring Schemas <https://marshmallow.readthedocs.io/en/latest/quickstart.html#declaring-schemas>`_
