#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import json

import opentracing
from cdumay_opentracing import SpanProxy
from cdumay_result import ResultSchema


class KserSpanProxy(SpanProxy):
    @classmethod
    def extract(cls, obj):
        """ Extract span context from the given object

        :param Any obj: Object to use as context
        :return: a SpanContext instance extracted from the inner span object or None if no
            such span context could be found.
        """
        trace = obj.metadata.get('__parent-span__', dict())
        if len(trace) > 0:
            return opentracing.tracer.extract(cls.FORMAT, obj.trace)

    @classmethod
    def inject(cls, span, obj):
        """ Injects the span context into a `carrier` object.

        :param opentracing.span.SpanContext span: the SpanContext instance
        :param Any obj: Object to use as context
        """
        obj.metadata['__parent-span__'] = dict()
        opentracing.tracer.inject(
            span, cls.FORMAT, obj.metadata['__parent-span__']
        )

    @classmethod
    def extract_tags(cls, obj):
        """ Extract tags from the given object

        :param Any obj: Object to use as context
        :return: Tags to add on span
        :rtype: dict
        """
        return dict(uuid=obj.uuid, entrypoint=obj.__class__.path)

    @classmethod
    def postrun(cls, span, obj, **kwargs):
        """ Trigger to execute just before closing the span

        :param opentracing.span.Span  span: the SpanContext instance
        :param Any obj: Object to use as context
        :param dict kwargs: additional data
        """
        for key, value in ResultSchema().dump(obj.result).items():
            if isinstance(value, (list, tuple, dict)):
                span.set_tag("result.{}".format(key), json.dumps(value))
            else:
                span.set_tag("result.{}".format(key), value)
