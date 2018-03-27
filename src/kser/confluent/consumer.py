#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import logging

# noinspection PyProtectedMember
# noinspection PyUnresolvedReferences
from confluent_kafka import Consumer as KafkaConsumer, KafkaError

from kser.controller import Controller

logger = logging.getLogger(__name__)


class Consumer(object):
    REGISTRY = Controller

    def __init__(self, config, topics):
        self.client = KafkaConsumer(config)
        self.client.subscribe(topics)

    def run(self):
        """ Run consumer
        """
        logger.info("{}.Starting...".format(self.__class__.__name__))
        running = True
        while running:
            msg = self.client.poll()
            if msg:
                # noinspection PyProtectedMember
                if not msg.error():
                    self.REGISTRY.run(msg.value().decode('utf-8'))
                elif msg.error().code() != KafkaError._PARTITION_EOF:
                    logger.error(msg.error())
                    running = False
        self.client.close()
