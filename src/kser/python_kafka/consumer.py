#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import logging
import os

from kafka import KafkaConsumer
from kser import KSER_METRICS_ENABLED
from kser.controller import Controller

logger = logging.getLogger(__name__)


class Consumer(object):
    REGISTRY = Controller

    def __init__(self, config, topics):
        self.client = KafkaConsumer(**config)
        self.client.subscribe(topics)

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
        for msg in self.client:
            data = msg.value.decode('utf-8')
            if self.client.config['enable_auto_commit'] is False:
                self.client.commit()
                logger.debug(
                    "{}: Manual commit done.".format(self.__class__.__name__)
                )
            self.REGISTRY.run(data)
