#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""

import logging

from cdumay_opentracing import OpenTracingSpan, OpenTracingManager
from kser import KSER_METRICS_ENABLED, KSER_TASK_COUNT
from kser.schemas import Message
from kser.sequencing.task import Task

logger = logging.getLogger(__name__)


class OpentracingTask(Task):
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
            out = self.prerun()
            OpenTracingManager.log_kv(span, self, "done")
            return out

    def _run(self):
        """ Execution body

        :return: Execution result
        :rtype: kser.result.Result
        """
        if KSER_METRICS_ENABLED == "yes":
            KSER_TASK_COUNT.inc()

        logger.debug(self.label("Run"), extra=dict(kmsg=Message(
            self.uuid, entrypoint=self.__class__.path,
            params=self.params, metadata=self.metadata
        ).dump()))

        with OpenTracingSpan(self, self.label("Run")) as span:
            out = self.run()
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
        """ un-wrapped execution, can raise excepetion

        :return: Execution result
        :rtype: kser.result.Result
        """
        if result:
            self.result += result

        with OpenTracingSpan(self, self.label("Execute")) as span:
            self._prerun()
            out = self._onsuccess(self._postrun(self._run()))
            OpenTracingManager.log_kv(span, self, "done")
            return out
