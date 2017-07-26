**********
Controller
**********

.. py:module:: kser.controller

The :class:`Controller` class is the message router:

#. It deserialize Kafka content
#. Check that the result is a :class:`kser.transport.Message`
#. Check that the ``message.entry`` is registered
#. Launch the entrypoint and ensure the result implement :class:`kser.result.Result`
#. If ``message.route`` is defined, the router store the result into a new :class:`kser.transport.Message` which can be sent using a :class:`kser.producer.Producer` object.

.. py:class:: Controller

    .. py:classmethod:: onforward(kmsg)

        If the message *kmsg* is a part of a workflow, this method is raised.

        :param kser.transport.Message kmsg: Kafka message
        :return: Execution result
        :rtype: :class:`kser.result.Result`

    .. py:classmethod:: register(name, entrypoint)

        Register a new entrypoint in the controller.

        :param str name: Key used by messages
        :param kser.entry.Entrypoint entrypoint: class to load
        :raises ValidationError: Invalid entry

    .. py:classmethod:: run(raw_data)

        Method representing the entrypoint's body.

        :param bytes raw_data: Kafka content as JSON
        :return: Execution result
        :rtype: :class:`kser.result.Result`

    .. py:classmethod:: onmessage(kmsg)

        Used when a message has been successfully deserialized.

        :param kser.transport.Message kmsg: Kafka message
        :return: Kafka message
        :rtype: :class:`kser.transport.Message`

    .. py:classmethod:: onsuccess(kmsg, result)

        This method is a wrapper called if the entrypoint execution succeed.

        :param kser.transport.Message kmsg: Kafka message
        :param kser.result.Result result: Execution result
        :return: Execution result
        :rtype: kser.result.Result

    .. py:classmethod:: onerror(kmsg, result)

        This method is a wrapper called if the entrypoint execution fail.

        :param kser.transport.Message kmsg: Kafka message
        :param kser.result.Result result: Execution result
        :return: Execution result
        :rtype: kser.result.Result
