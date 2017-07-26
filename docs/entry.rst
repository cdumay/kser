**********
Entrypoint
**********

.. py:module:: kser.entry

An *entrypoint* is a "job" or a "task" to execute.

.. py:class:: Entrypoint

    This class is intended to be implemented for your needs. A `entrypoint` is available only if it has been registred in the controller using :meth:`kser.controller.Controller.register`.

    .. py:classmethod:: prerun(kmsg)

        This method is a wrapper called **before** the call of the execution body.

        :param kser.transport.Message kmsg: Kafka message
        :return: Kafka message
        :rtype: kser.transport.Message

    .. py:classmethod:: postrun(kmsg, result)

        This method is a wrapper called **after** the call of the execution body.

        :param kser.transport.Message kmsg: Kafka message
        :param kser.result.Result result: Execution result
        :return: Execution result
        :rtype: kser.result.Result

    .. py:classmethod:: run(uuid, result, **kwargs)

        The body execution. You may override this method in a subclass.

        :param str uuid: Message UUID
        :param kser.result.Result result: Previous result
        :param dict kwargs: Parameters
        :return: Execution result
        :rtype: kser.result.Result

        .. note::

            `**kwargs` should be replaced by defined arguments to facilitate code reading and perform a minimal code check.

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


Example::

    from kser import __hostname__
    from kser.entry import Entrypoint
    from kser.result import Result


    class Hello(Entrypoint):
        @classmethod
        def run(cls, uuid, result, remote):
            """ A usefull entrypoint !

            :param str uuid: Message UUID
            :param kser.result.Result result: Previous result
            :param str remote: The remote host
            :return: Execution result
            :rtype: kser.result.Result
            """
            return Result(
                uuid=uuid, stdout="Hello '{}', my name is '{}'".format(remote, __hostname__),
                retval=dict(hostname=__hostname__)
            )