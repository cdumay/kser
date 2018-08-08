#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import logging

from kser.schemas import Message
from kser.sequencing.operation import Operation
from kser.tracing import OpentracingBase, OpentracingTracer
from opentracing import Format

logger = logging.getLogger(__name__)


class OpentracingOperation(Operation, OpentracingBase):
    def __init__(self, uuid=None, status="PENDING", params=None, tasks=None,
                 result=None, metadata=None):
        OpentracingBase.__init__(self, uuid, params, status, result, metadata)
        self.tasks = tasks or list()

    def _prerun(self):
        """ To execute before running message

        :return: Kafka message
        :rtype: kser.schemas.Message
        """
        logger.debug(self.label("PreRun"), extra=dict(kmsg=Message(
            self.uuid, entrypoint=self.__class__.path,
            params=self.params, metadata=self.metadata
        ).dump()))

        with self.create_span('PreRun') as span:
            self.check_required_params()
            self._set_status("RUNNING")
            out = self.prerun()
            span.log_kv(dict(event="done"))
            return out

    def _postrun(self, result):
        """ To execute after exection

        :param kser.result.Result result: Execution result
        :return: Execution result
        :rtype: kser.result.Result
        """
        logger.debug(self.label("PostRun"), extra=dict(kmsg=Message(
            self.uuid, entrypoint=self.__class__.path,
            params=self.params, metadata=self.metadata
        ).dump()))

        with self.create_span('PostRun') as span:
            out = self.postrun(result)
            span.log_kv(dict(event="done."))
            return out

    def unsafe_execute(self, result=None):
        with self.create_root_span("Execute") as span:
            span.log_kv(dict(event="starting..."))
            self._prerun()
            for task in self.tasks:
                span_ctx = dict()
                OpentracingTracer.get_tracer().inject(
                    span, Format.TEXT_MAP, span_ctx
                )
                task.set_parent_span(span_ctx)
                result = task.unsafe_execute(result=result)
                if result.retcode != 0:
                    return self._onerror(result)

            result = self._onsuccess(self._postrun(result=result))
            span.log_kv(dict(event="done."))
            return result
