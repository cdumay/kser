#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import logging
import opentracing

from kser.schemas import Message
from kser.sequencing.operation import Operation
from kser.tracing.proxy import KserSpan

logger = logging.getLogger(__name__)


class OpentracingOperation(Operation):
    def unsafe_execute(self, result=None):
        with opentracing.tracer.start_span(
                obj=self, operation_name=self.label("Execute"),
                span_factory=KserSpan) as span:
            for task in self.tasks:
                KserSpan.inject(span, task)
                result = task.unsafe_execute(result=result)
                if result.retcode != 0:
                    return self._onerror(result)

            self.result = self._onsuccess(self._postrun(result=result))
            span.obj = self
            return self.result

    # noinspection PyPep8Naming
    def to_Message(self, result=None):
        """ Entrypoint -> Message

        :param kser.result.Result result: Execution result
        :return: Kafka message
        :rtype kser.schemas.Message
        """
        if opentracing.tracer.current_span:
            KserSpan.inject(opentracing.tracer.current_span, self)

        return Message(
            uuid=self.uuid, entrypoint=self.__class__.path, params=self.params,
            result=result if result else self.result, metadata=self.metadata
        )
