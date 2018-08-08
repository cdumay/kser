#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""

import logging

from kser import KSER_METRICS_ENABLED, KSER_TASK_COUNT
from kser.schemas import Message
from kser.tracing import OpentracingBase

logger = logging.getLogger(__name__)


class OpentracingTask(OpentracingBase):

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
            out = self.prerun()
            span.log_kv(dict(event="done"))
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

        with self.create_span('Run') as span:
            out = self.run()
            span.log_kv(dict(event="done."))
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
        """ un-wrapped execution, can raise excepetion

        :return: Execution result
        :rtype: kser.result.Result
        """
        if result:
            self.result += result

        with self.create_root_span("Execute") as span:
            self._prerun()
            out = self._onsuccess(self._postrun(self._run()))
            span.log_kv(dict(event="done."))
            return out
