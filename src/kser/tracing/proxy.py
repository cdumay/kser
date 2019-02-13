#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import json
import re

import opentracing
from cdumay_opentracing import Span
from cdumay_result import ResultSchema


class KserSpan(Span):
    EXCLUDE_PATTERNS = ['.*(password|PASSWORD).*', '.*(token|TOKEN).*']

    @classmethod
    def name(cls, obj):
        return str(obj.__class__.path)

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
            if isinstance(value, dict):
                try:
                    flat_data = cls.filter_keys(
                        cls.fix_additional_fields(value)
                    )
                    span.set_tag("result.{}".format(key), json.dumps(flat_data))
                except Exception:
                    span.set_tag("result.{}".format(key), "N/A")
            elif isinstance(value, (list, tuple)):
                try:
                    span.set_tag("result.{}".format(key), json.dumps(value))
                except Exception:
                    try:
                        span.set_tag("result.{}".format(key), value)
                    except Exception:
                        span.set_tag("result.{}".format(key), "N/A")
            else:
                span.set_tag("result.{}".format(key), value)

    @staticmethod
    def fix_additional_fields(data):
        """description of fix_additional_fields"""
        result = dict()
        for key, value in data.items():
            if isinstance(value, dict):
                result.update(KserSpan.to_flat_dict(key, value))
            else:
                result[key] = value
        return result

    @staticmethod
    def key_path(*args):
        """description of key_path"""
        return "_".join(args)

    @staticmethod
    def to_flat_dict(prefix, data):
        flat_result = dict()
        for dkey, dvalue in data.items():
            path = KserSpan.key_path(prefix, dkey)
            if isinstance(dvalue, dict):
                flat_result.update(KserSpan.to_flat_dict(path, dvalue))
            else:
                flat_result[path] = dvalue
        return flat_result

    @classmethod
    def filter_keys(cls, data):
        """Filter GELF record keys using exclude_patterns

        :param dict data: Log record has dict
        :return: the filtered log record
        :rtype: dict
        """
        keys = list(data.keys())
        for pattern in cls.EXCLUDE_PATTERNS:
            for key in keys:
                if re.match(pattern, key):
                    keys.remove(key)
        return dict(filter(lambda x: x[0] in keys, data.items()))
