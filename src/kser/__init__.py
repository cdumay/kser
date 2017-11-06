#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import logging
import socket

__hostname__ = socket.gethostname()

logger = logging.getLogger(__name__)


class BaseSerializer(object):
    @classmethod
    def _onsuccess(cls, kmsg, result):
        """ To execute on execution success

        :param kser.transport.Message kmsg: Kafka message
        :param kser.result.Result result: Execution result
        :return: Execution result
        :rtype: kser.result.Result
        """
        logger.info("{}.Success: {}[{}]: {}".format(
            cls.__name__, kmsg.entrypoint, kmsg.uuid, result
        ))
        return cls.onsuccess(kmsg, result)

    @classmethod
    def onsuccess(cls, kmsg, result):
        """ To execute on execution success

        :param kser.transport.Message kmsg: Kafka message
        :param kser.result.Result result: Execution result
        :return: Execution result
        :rtype: kser.result.Result
        """
        return result

    @classmethod
    def _onerror(cls, kmsg, result):
        """ To execute on execution failure

        :param kser.transport.Message kmsg: Kafka message
        :param kser.result.Result result: Execution result
        :return: Execution result
        :rtype: kser.result.Result
        """
        logger.error("{}.Failed: {}[{}]: {}".format(
            cls.__name__, kmsg.entrypoint, kmsg.uuid, result
        ), extra=result.retval)
        return cls.onerror(kmsg, result)

    @classmethod
    def onerror(cls, kmsg, result):
        """ To implement

        :param kser.transport.Message kmsg: Kafka message
        :param kser.result.Result result: Execution result
        :return: Execution result
        :rtype: kser.result.Result
        """
        return result


class BaseTransportSerializer(BaseSerializer):
    @classmethod
    def _onmessage(cls, kmsg):
        """ Call on received message

        :param kser.transport.Message kmsg: Kafka message
        :return: Kafka message
        :rtype: kser.transport.Message
        """
        logger.debug("{}.ReceivedMessage: {}[{}]".format(
            cls.__name__, kmsg.entrypoint, kmsg.uuid
        ))
        return cls.onmessage(kmsg)

    @classmethod
    def onmessage(cls, kmsg):
        """ To implement

        :param kser.transport.Message kmsg: Kafka message
        :return: Kafka message
        :rtype: kser.transport.Message
        """
        return kmsg
