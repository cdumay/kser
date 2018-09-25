#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import json

import opentracing
from cdumay_opentracing import Span
from cdumay_result import ResultSchema


class KserSpan(Span):
    @classmethod
    def name(cls, obj):
        return obj(obj.__class__.path)

    @classmethod
    def extract_span(cls, obj):
        trace = obj.metadata.get('__parent-span__', dict())
        if len(trace) > 0:
            return cls.span_from_dict(trace)

    @classmethod
    def inject_span(cls, span, obj):
        obj.metadata['__parent-span__'] = cls.span_serialize(span)

    @classmethod
    def extract(cls, obj):
        """ Extract span context from the given object

        :param Any obj: Object to use as context
        :return: a SpanContext instance extracted from the inner span object or None if no
            such span context could be found.
        """
        span = cls.extract_span(obj)
        if span:
            return span.context

    @classmethod
    def inject(cls, span, obj):
        """ Injects the span context into a `carrier` object.

        :param opentracing.span.SpanContext span: the SpanContext instance
        :param Any obj: Object to use as context
        """
        obj.metadata['__parent-span__'] = dict()
        cls.inject_span(span, obj.metadata['__parent-span__'])

    @classmethod
    def extract_tags(cls, obj):
        """ Extract tags from the given object

        :param Any obj: Object to use as context
        :return: Tags to add on span
        :rtype: dict
        """
        return dict(uuid=obj.uuid, entrypoint=obj.__class__.path)

    @classmethod
    def _postrun(cls, span, obj, **kwargs):
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
