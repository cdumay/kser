#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import logging
from uuid import uuid4

from kser import BaseSerializer
from cdumay_result import Result
from kser.transport import Message

logger = logging.getLogger(__name__)


class EntrypointMeta(type):
    @property
    def path(cls):
        return "{}.{}".format(cls.__module__, cls.__name__)


class Entrypoint(BaseSerializer, metaclass=EntrypointMeta):
    @classmethod
    def _prerun(cls, kmsg):
        """ To execute before running message

        :param kser.transport.Message kmsg: Kafka message
        :return: Kafka message
        :rtype: kser.transport.Message
        """
        logger.debug("{}.PreRun: {}[{}]".format(
            cls.__name__, kmsg.entrypoint, kmsg.uuid
        ))
        return cls.prerun(kmsg)

    @classmethod
    def prerun(cls, kmsg):
        """ To implement

        :param kser.transport.Message kmsg: Kafka message
        :return: Kafka message
        :rtype: kser.transport.Message
        """
        return kmsg

    @classmethod
    def _postrun(cls, kmsg, result):
        """ To execute after exection

        :param kser.transport.Message kmsg: Kafka message
        :param kser.result.Result result: Execution result
        :return: Execution result
        :rtype: kser.result.Result
        """
        logger.debug("{}.PostRun: {}[{}]".format(
            cls.__name__, kmsg.entrypoint, kmsg.uuid
        ))
        return cls.postrun(kmsg, result)

    @classmethod
    def postrun(cls, kmsg, result):
        """ To implement

        :param kser.transport.Message kmsg: Kafka message
        :param kser.result.Result result: Execution result
        :return: Execution result
        :rtype: kser.result.Result
        """
        return result

    @classmethod
    def _run(cls, kmsg):
        """ Execution body

        :param kser.transport.Message kmsg: Kafka message
        :return: Execution result
        :rtype: kser.result.Result
        """
        logger.debug("{}.Run: {}[{}]".format(
            cls.__name__, kmsg.entrypoint, kmsg.uuid
        ))
        return cls.run(uuid=kmsg.uuid, result=kmsg.result, **kmsg.params)

    @classmethod
    def run(cls, uuid, result, **kwargs):
        """ To implement

        :param str uuid: Message UUID
        :param kser.result.Result result: Previous result
        :param dict kwargs: Parameters
        :return: Execution result
        :rtype: kser.result.Result
        """
        return Result(uuid=uuid, retval=kwargs)

    @classmethod
    def execute(cls, kmsg):
        """ Execution 'wrapper' to make sure that it return a result

        :param kser.transport.Message kmsg: Kafka message
        :return: Execution result
        :rtype: kser.result.Result
        """
        try:
            result = cls._onsuccess(
                kmsg, cls._postrun(kmsg, cls._run(cls._prerun(kmsg)))
            )

        except Exception as exc:
            result = cls._onerror(
                kmsg, Result.fromException(exc, uuid=kmsg.uuid)
            )

        finally:
            return result

    @classmethod
    def as_kmsg(cls, uuid=None, params=None, result=None):
        if not uuid:
            uuid = str(uuid4())
        if not params:
            params = dict()

        return Message(
            uuid=uuid, entrypoint=cls.path, params=params, result=result
        )
