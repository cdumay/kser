#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import logging
import opentracing

from kser.sequencing.operation import Operation
from kser.tracing.proxy import KserSpan

logger = logging.getLogger(__name__)


class OpentracingOperation(Operation):
    def unsafe_execute(self, result=None):
        with opentracing.tracer.start_span(
                obj=self, child_of=KserSpan.extract_span(self),
                operation_name=self.label("Execute"),
                span_factory=KserSpan) as span:
            for task in self.tasks:
                KserSpan.inject_span(span, task)
                result = task.unsafe_execute(result=result)
                if result.retcode != 0:
                    return self._onerror(result)

            self.result = self._onsuccess(self._postrun(result=result))
            span.obj = self
            return self.result
