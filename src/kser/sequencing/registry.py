#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import logging
from kser.controller import Controller

logger = logging.getLogger(__name__)


class OperationRegistry(object):
    def __init__(self, app=None, controller_class=Controller):
        self.controller = controller_class()
        self.app = None
        if app:
            self.init_app(app)

    def subscribe(self, callback):
        if callback.path not in self.controller.ENTRYPOINTS:
            logger.info("Operation registry: loaded {}".format(callback.path))
            self.controller.register(callback.path, callback)

    def init_app(self, app=None):
        self.app = app
        self.load_tasks()

    def load_tasks(self):
        """ To implement, load operation tasks

        :return:
        """
