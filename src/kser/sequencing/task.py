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
                 metadata=None):
        """ A task is a :class:`kser.entry.Entrypoint` with additional attributes.

        :param str uuid: task unique identifier
        :param dict params: task parameter
        :param str status: task status
        :param cdumay_result.Result result: forwarded result from a previous task
        :param dict metadata: task context
        """
        self.status = status
        Entrypoint.__init__(
            self, uuid=uuid, params=params, result=result, metadata=metadata
        )

    def get_attr(self, item):
        attr = "{}Id".format(item)
        return attr, getattr(getattr(self, item, self), attr, None)

    def log(self, message, level=logging.INFO, *args, **kwargs):
        """ Send log entry

        :param str message: log message
        :param int level: `Logging level <https://docs.python.org/3/library/logging.html#levels>`_
        :param list args: log record arguments
        :param dict kwargs: log record key argument
        """
        msg = "{}.{}: {}[{}]: {}".format(
            self.__class__.__name__, self.status, self.__class__.path,
            self.uuid, message
        )
        extra = kwargs.pop("extra", dict())
        extra.update(dict(kmsg=Message(
            self.uuid, entrypoint=self.__class__.path, params=self.params,
            metadata=self.metadata
        ).dump()))

        return logger.log(
            level=level, msg=msg, extra=extra, *args, **kwargs
        )

    def __repr__(self):
        return "Task [{}](uuid={},status={}, params={})".format(
            self.__class__.path, self.uuid, self.status, self.params
        )
