#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import logging
from uuid import uuid4

from cdumay_error import ValidationError
from cdumay_result import Result, ResultSchema
from kser.schemas import Message

logger = logging.getLogger(__name__)


class EntrypointMeta(type):
    @property
    def path(cls):
        return "{}.{}".format(cls.__module__, cls.__name__)


class Entrypoint(object, metaclass=EntrypointMeta):
    REQUIRED_FIELDS = ()

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
        self._post_init()

    def _post_init(self):
        """A post init trigger"""
        try:
            return self.postinit()
        except Exception as exc:
            return self._onerror(Result.from_exception(exc, uuid=self.uuid))

    def postinit(self):
        """"""

    def check_required_params(self):
        """ Check if all required parameters are set"""
        for param in self.REQUIRED_FIELDS:
            if param not in self.params:
                raise ValidationError("Missing parameter: {}".format(param))

    def _onsuccess(self, result):
        """ To execute on execution success

        :param kser.result.Result result: Execution result
        :return: Execution result
        :rtype: kser.result.Result
        """
        if result:
            result = self.result + result
        else:
            result = self.result
        logger.info(
            "{}.Success: {}[{}]: {}".format(
                self.__class__.__name__, self.__class__.path, self.uuid, result
            ),
            extra=dict(
                kmsg=Message(
                    self.uuid, entrypoint=self.__class__.path,
                    params=self.params
                ).dump(),
                kresult=ResultSchema().dump(result) if result else dict()
            )
        )
        return self.onsuccess(result)

    def log(self, message, level=logging.INFO, *args, **kwargs):
        msg = "{}.MESSAGE: {}[{}]: {}".format(
            self.__class__.__name__, self.__class__.path, self.uuid, message
        )
        return logger.log(level=level, msg=msg, *args, **kwargs)

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
        if result:
            result = self.result + result
        else:
            result = self.result
        logger.error(
            "{}.Failed: {}[{}]: {}".format(
                self.__class__.__name__, self.__class__.path, self.uuid, result
            ),
            extra=dict(
                kmsg=Message(
                    self.uuid, entrypoint=self.__class__.path,
                    params=self.params
                ).dump(),
                kresult=ResultSchema().dump(result) if result else dict()
            )
        )
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
        logger.debug(
            "{}.PreRun: {}[{}]".format(
                self.__class__.__name__, self.__class__.path, self.uuid
            ),
            extra=dict(
                kmsg=Message(
                    self.uuid, entrypoint=self.__class__.path,
                    params=self.params
                ).dump()
            )
        )
        self.check_required_params()
        return self.prerun()

    def prerun(self):
        """ To implement"""

    def _postrun(self, result):
        """ To execute after exection

        :param kser.result.Result result: Execution result
        :return: Execution result
        :rtype: kser.result.Result
        """
        logger.debug(
            "{}.PostRun: {}[{}]".format(
                self.__class__.__name__, self.__class__.path, self.uuid
            ),
            extra=dict(
                kmsg=Message(
                    self.uuid, entrypoint=self.__class__.path,
                    params=self.params
                ).dump()
            )
        )
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
        logger.debug(
            "{}.Run: {}[{}]".format(
                self.__class__.__name__, self.__class__.path, self.uuid
            ),
            extra=dict(
                kmsg=Message(
                    self.uuid, entrypoint=self.__class__.path,
                    params=self.params
                ).dump()
            )
        )
        return self.run()

    def run(self):
        """ To implement

        :return: Execution result
        :rtype: kser.result.Result
        """
        raise NotImplemented("Task '{}' not implemented".format(
            self.__class__.path
        ))

    def unsafe_execute(self, result=None):
        """ un-wrapped execution, can raise excepetion

        :return: Execution result
        :rtype: kser.result.Result
        """
        if result:
            self.result += result

        self._prerun()
        return self._onsuccess(self._postrun(self._run()))

    def execute(self, result=None):
        """ Execution 'wrapper' to make sure that it return a result

        :return: Execution result
        :rtype: kser.result.Result
        """
        try:
            return self.unsafe_execute(result=result)
        except Exception as exc:
            return self._onerror(Result.from_exception(exc, uuid=self.uuid))

    # noinspection PyPep8Naming
    def to_Message(self, result=None):
        """ Entrypoint -> Message

        :param kser.result.Result result: Execution result
        :return: Kafka message
        :rtype kser.schemas.Message
        """
        return Message(
            uuid=self.uuid, entrypoint=self.__class__.path, params=self.params,
            result=result if result else self.result
        )

    # noinspection PyPep8Naming
    @classmethod
    def from_Message(cls, kmsg):
        """ Message -> Entrypoint

        :param kser.schemas.Message kmsg: Kafka message
        :return: a entrypoint
        :rtype kser.entry.Entrypoint
        """
        return cls(uuid=kmsg.uuid, params=kmsg.params, result=kmsg.result)
