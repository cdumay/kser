#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import logging
from kser.entry import Entrypoint
from kser.schemas import Message

logger = logging.getLogger(__name__)


class Task(Entrypoint):
    """"""

    @classmethod
    def init_by_id(cls, _id):
        """Load task by its ID"""

    def __init__(self, uuid=None, params=None, status="PENDING", result=None,
                 **kwargs):
        self.status = status
        self.metadata = kwargs

        Entrypoint.__init__(self, uuid=uuid, params=params, result=result)

    def get_attr(self, item):
        attr = "{}Id".format(item)
        return attr, getattr(getattr(self, item, self), attr, None)

    def log(self, message, level=logging.INFO, *args, **kwargs):
        msg = "{}.{}: {}[{}]: {}".format(
            self.__class__.__name__, self.status, self.__class__.path,
            self.uuid, message
        )
        extra = kwargs.pop("extra", dict())
        extra.update(dict(kmsg=Message(
            self.uuid, entrypoint=self.__class__.path, params=self.params
        ).dump()))

        return logger.log(
            level=level, msg=msg, extra=extra, *args, **kwargs
        )

    def __repr__(self):
        return "Task [{}](uuid={},status={}, params={})".format(
            self.__class__.path, self.uuid, self.status, self.params
        )
