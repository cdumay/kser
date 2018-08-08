#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import os

import opentracing
from jaeger_client import Config
from kser.entry import EntrypointMeta
from kser.sequencing.task import Task
from opentracing import Format


class OpentracingTracer(object):
    _tracer = None

    @staticmethod
    def get_tracer():
        if OpentracingTracer._tracer is None:
            cfg = Config(service_name="kser", config={
                'sampler': {'type': 'const', 'param': 1}, 'logging': True,
                'local_agent': {
                    'reporting_host': os.getenv('JAEGER_HOST', 'localhost')
                }
            })
            if cfg.initialized() is True:
                OpentracingTracer._tracer = opentracing.tracer
            else:
                OpentracingTracer._tracer = cfg.initialize_tracer()
        return OpentracingTracer._tracer


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
            span_ctx = OpentracingTracer.get_tracer().extract(
                Format.TEXT_MAP, self._span
            )

        return OpentracingTracer.get_tracer().start_span(
            self.label(action), span_ctx
        )

    def create_root_span(self, action=None):
        span = self.create_span(action)
        OpentracingTracer.get_tracer().inject(span, Format.TEXT_MAP, self._span)
        return span
