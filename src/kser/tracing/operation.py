#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import logging

from cdumay_opentracing import OpenTracingManager
from kser.schemas import Message
from kser.sequencing.operation import Operation
from kser.tracing.proxy import KserSpanProxy

logger = logging.getLogger(__name__)


class OpentracingOperation(Operation):
    def unsafe_execute(self, result=None):
        with OpenTracingManager.create_span(self, self.label("Execute")):
            self._prerun()
            for task in self.tasks:
                result = task.unsafe_execute(result=result)
                if result.retcode != 0:
                    return self._onerror(result)

            self.result = self._onsuccess(self._postrun(result=result))
            return self.result

    # noinspection PyPep8Naming
    def to_Message(self, result=None):
        """ Entrypoint -> Message

        :param kser.result.Result result: Execution result
        :return: Kafka message
        :rtype kser.schemas.Message
        """
        current_span = OpenTracingManager.get_current_span(self)
        if current_span:
            KserSpanProxy.inject(current_span, self)

        return Message(
            uuid=self.uuid, entrypoint=self.__class__.path, params=self.params,
            result=result if result else self.result, metadata=self.metadata
        )
