******
Result
******

.. py:module:: kser.result

.. py:class:: Result(retcode=0, stdout="", stderr="", retval=None, uuid=None)

    A class to store process execution data.

    :param int retcode: A return code based on HTTP response status. `0` is allowed too.
    :param str stdout: The standard execution output
    :param str stderr: The error execution output.
    :param dict retval: Additionnal result stored in `dict`
    :param str uuid: Current Kafka :class:`kser.transport.Message` uuid

    .. warning::

        Unlike process execution return code, a :class:`kser.result.Result` is considered successfull if `retcode` is lower than **300** including `0`.

    .. py:method:: print(data)

        Store text in result's stdout

        :param Any data: Any printable data

    .. py:method:: print_err(data)

        Store text in result's stderr

        :param Any data: Any printable data

    .. py:staticmethod:: fromException(exc, uuid=None)

        Serialize an exception into a result

        :param Exception exc: Exception raised
        :param str uuid: Current Kafka :class:`kser.transport.Message` uuid
        :rtype: :class:`kser.result.Result`

