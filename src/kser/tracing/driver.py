#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import opentracing
from cdumay_opentracing import OpenTracingDriver
from cdumay_result import ResultSchema


class OpenTracingKserDriver(OpenTracingDriver):
    @classmethod
    def extract(cls, data):
        trace = data.metadata.get('__parent-span__', dict())
        if len(trace) > 0:
            return opentracing.tracer.extract(cls.FORMAT, data.trace)

    @classmethod
    def inject(cls, span, data):
        data.metadata['__parent-span__'] = dict()
        opentracing.tracer.inject(
            span, cls.FORMAT, data.metadata['__parent-span__']
        )

    @classmethod
    def tags(cls, data):
        return dict(uuid=data.uuid, entrypoint=data.__class__.path)

    @classmethod
    def log_kv(cls, span, data, event, **kwargs):
        return span.log_kv({
            "event": event, **ResultSchema().dump(data.result), **kwargs
        })
