#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import logging
from confluent_kafka import Consumer as ConfluentConsumer, KafkaError
from kser.controller import Controller

logger = logging.getLogger("kser")


class Consumer(object):
    REGISTRY = Controller

    def __init__(self, config, topics):
        cfg = {
            'ssl.ca.location': '/etc/ssl/certs',
            'security.protocol': 'sasl_ssl',
            'api.version.request': True,
            'sasl.mechanisms': "PLAIN",
            'default.topic.config': {'auto.offset.reset': 'smallest'}
        }
        cfg.update(config or dict())
        self.client = ConfluentConsumer(cfg)
        self.client.subscribe(topics)

    def run(self):
        """ Run consumer
        """
        logger.info("{}.Starting...".format(self.__class__.__name__))
        running = True
        while running:
            msg = self.client.poll()
            if not msg.error():
                self.REGISTRY.run(msg.value().decode('utf-8'))
            elif msg.error().code() != KafkaError._PARTITION_EOF:
                logger.critical("{}.PARTITION_EOF: {}".format(
                    self.__class__.__name__, msg.error()
                ))
                running = False

        self.client.close()
