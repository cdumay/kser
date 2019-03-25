#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import logging
import os
import time

from kafka import KafkaConsumer
from kser import KSER_METRICS_ENABLED
from kser.controller import Controller

logger = logging.getLogger(__name__)


class Consumer(object):
    REGISTRY = Controller

    def __init__(self, config, topics):
        self.client = KafkaConsumer(**config)
        self.client.subscribe(topics)
        self.clean_lock()

    def __del__(self):
        for lockfile in (os.environ['LOCK_FILE'], os.environ['RUNNING_FILE']):
            if os.path.exists(lockfile):
                logger.debug("Cleaning existing lock file: {}".format(lockfile))
                os.remove(lockfile)

    def clean_lock(self):
        if os.path.exists(os.environ['LOCK_FILE']):
            logger.debug("Cleaning existing pause file: {}".format(
                os.environ['LOCK_FILE']
            ))
            os.remove(os.environ['LOCK_FILE'])

    def is_active(self):
        return not os.path.exists(os.environ['LOCK_FILE'])

    def run(self):
        """ Run consumer
        """
        if KSER_METRICS_ENABLED == "yes":
            from prometheus_client import start_http_server
            logger.info("Metric.Starting...")
            start_http_server(
                os.getenv("KSER_METRICS_PORT", 8888),
                os.getenv("KSER_METRICS_ADDRESS", "0.0.0.0")
            )

        logger.info("{}.Starting...".format(self.__class__.__name__))

        while True:
            if self.is_active() is True:
                msg = next(self.client)
                data = msg.value.decode('utf-8')
                if self.client.config['enable_auto_commit'] is False:
                    self.client.commit()
                    logger.debug("{}: Manual commit done.".format(
                        self.__class__.__name__
                    ))
                self.REGISTRY.run(data)
            else:
                logger.warning("Consumer is paused")
                time.sleep(60)
