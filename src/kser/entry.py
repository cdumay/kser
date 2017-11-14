#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import logging
from uuid import uuid4
from cdumay_result import Result

from kser.schemas import Message

logger = logging.getLogger(__name__)


class EntrypointMeta(type):
    @property
    def path(cls):
        return "{}.{}".format(cls.__module__, cls.__name__)


class Entrypoint(object, metaclass=EntrypointMeta):
    def __init__(self, uuid=None, params=None, result=None):
        if not uuid:
            uuid = str(uuid4())
        if not params:
            params = dict()
        if not result:
            result = Result(uuid=uuid)

        self.uuid = uuid
        self.params = params
        self.result = result

    def _onsuccess(self, result):
        """ To execute on execution success

        :param kser.result.Result result: Execution result
        :return: Execution result
        :rtype: kser.result.Result
        """
        logger.info("{}.Success: {}[{}]: {}".format(
            self.__class__.__name__, self.__class__.path, self.uuid, result
        ))
        return self.onsuccess(result)

    def onsuccess(self, result):
        """ To execute on execution success

        :param kser.result.Result result: Execution result
        :return: Execution result
        :rtype: kser.result.Result
        """
        return result

    def _onerror(self, result):
        """ To execute on execution failure

        :param kser.result.Result result: Execution result
        :return: Execution result
        :rtype: kser.result.Result
        """
        logger.error("{}.Failed: {}[{}]: {}".format(
            self.__class__.__name__, self.__class__.path, self.uuid, result
        ), extra=result.retval)
        return self.onerror(result)

    def onerror(self, result):
        """ To implement

        :param kser.result.Result result: Execution result
        :return: Execution result
        :rtype: kser.result.Result
        """
        return result

    def _prerun(self):
        """ To execute before running message

        :return: Kafka message
        :rtype: kser.schemas.Message
        """
        logger.debug("{}.PreRun: {}[{}]".format(
            self.__class__.__name__, self.__class__.path, self.uuid
        ))
        return self.prerun()

    def prerun(self):
        """ To implement"""

    def _postrun(self, result):
        """ To execute after exection

        :param kser.result.Result result: Execution result
        :return: Execution result
        :rtype: kser.result.Result
        """
        logger.debug("{}.PostRun: {}[{}]".format(
            self.__class__.__name__, self.__class__.path, self.uuid
        ))
        return self.postrun(result)

    def postrun(self, result):
        """ To implement

        :param kser.result.Result result: Execution result
        :return: Execution result
        :rtype: kser.result.Result
        """
        return result

    def _run(self):
        """ Execution body

        :return: Execution result
        :rtype: kser.result.Result
        """
        logger.debug("{}.Run: {}[{}]".format(
            self.__class__.__name__, self.__class__.path, self.uuid
        ))
        return self.run()

    def run(self):
        """ To implement

        :return: Execution result
        :rtype: kser.result.Result
        """
        return Result(uuid=self.uuid)

    def execute(self):
        """ Execution 'wrapper' to make sure that it return a result

        :return: Execution result
        :rtype: kser.result.Result
        """
        try:
            self._prerun()
            result = self._onsuccess(self._postrun(self._run()))

        except Exception as exc:
            result = self._onerror(Result.fromException(exc, uuid=self.uuid))

        finally:
            # noinspection PyUnboundLocalVariable
            return result

    def to_Message(self, result=None):
        """ Entrypoint -> Message

        :param kser.result.Result result: Execution result
        :return: Kafka message
        :rtype kser.schemas.Message
        """
        return Message(
            uuid=self.uuid, entrypoint=self.__class__.path, params=self.params,
            result=self.result if self.result else result
        )

    @classmethod
    def from_Message(cls, kmsg):
        """ Message -> Entrypoint

        :param kser.schemas.Message kmsg: Kafka message
        :return: a entrypoint
        :rtype kser.entry.Entrypoint
        """
        return cls(uuid=kmsg.uuid, params=kmsg.params, result=kmsg.result)
