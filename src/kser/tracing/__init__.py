#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import os

from jaeger_client import Config
from kser.entry import EntrypointMeta
from kser.sequencing.task import Task
from opentracing import Format

TRACER = Config(service_name="kser", config={
    'sampler': {'type': 'const', 'param': 1}, 'logging': True,
    'local_agent': {'reporting_host': os.getenv('JAEGER_HOST', 'localhost')}
}).initialize_tracer()


class OpentracingBase(Task, metaclass=EntrypointMeta):
    def __init__(self, uuid=None, params=None, status="PENDING", result=None,
                 metadata=None):
        Task.__init__(self, uuid, params, status, result, metadata)
        self._span = dict()
        self.set_parent_span(
            self.metadata.get('__parent-span__', dict())
        )

    def set_parent_span(self, parent):
        self._span = parent

    def label(self, action=None):
        return "{}[{}]{}".format(
            self.__class__.__name__, self.uuid,
            " - {}".format(action) if action else ""
        )

    def create_span(self, action=None):
        span_ctx = None
        if len(self._span) != 0:
            span_ctx = TRACER.extract(Format.TEXT_MAP, self._span)

        return TRACER.start_span(self.label(action), span_ctx)

    def create_root_span(self, action=None):
        span = self.create_span(action)
        TRACER.inject(span, Format.TEXT_MAP, self._span)
        return span
