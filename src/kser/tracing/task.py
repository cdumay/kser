#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""

import logging

import opentracing
from kser.sequencing.task import Task
from kser.tracing.proxy import KserSpan

logger = logging.getLogger(__name__)


class OpentracingTask(Task):
    def unsafe_execute(self, result=None):
        """ un-wrapped execution, can raise excepetion

        :return: Execution result
        :rtype: kser.result.Result
        """
        if result:
            self.result += result

        with opentracing.tracer.start_span(
                obj=self, child_of=KserSpan.extract_span(self),
                span_factory=KserSpan) as span:
            self.result = self._onsuccess(self._postrun(self._run()))
            span.obj = self
            return self.result
