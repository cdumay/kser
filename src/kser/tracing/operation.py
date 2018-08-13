#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import logging

from cdumay_opentracing import OpenTracingSpan, OpenTracingManager
from kser.schemas import Message
from kser.sequencing.operation import Operation

logger = logging.getLogger(__name__)


class OpentracingOperation(Operation):
    def _prerun(self):
        """ To execute before running message

        :return: Kafka message
        :rtype: kser.schemas.Message
        """
        logger.debug(self.label("PreRun"), extra=dict(kmsg=Message(
            self.uuid, entrypoint=self.__class__.path,
            params=self.params, metadata=self.metadata
        ).dump()))

        with OpenTracingSpan(self, self.label("PreRun")) as span:
            self.check_required_params()
            self._set_status("RUNNING")
            out = self.prerun()
            OpenTracingManager.log_kv(span, self, "done")
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

        with OpenTracingSpan(self, self.label("PostRun")) as span:
            out = self.postrun(result)
            OpenTracingManager.log_kv(span, self, "done")
            return out

    def unsafe_execute(self, result=None):
        with OpenTracingSpan(self, self.label("Execute")) as span:
            span.log_kv(dict(event="starting..."))
            self._prerun()
            for task in self.tasks:
                result = task.unsafe_execute(result=result)
                if result.retcode != 0:
                    return self._onerror(result)

            result = self._onsuccess(self._postrun(result=result))
            OpenTracingManager.log_kv(span, self, "done")
            return result
