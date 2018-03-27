#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import time
import logging
from cdumay_rest_client.client import RESTClient
from kser.controller import Controller

logger = logging.getLogger(__name__)


class LoopInfo(object):
    def __init__(self, sleep):
        self.sleep = sleep


class Consumer(object):
    REGISTRY = Controller

    def __init__(self, config, topics):
        self.client = RESTClient(
            server=config["bootstrap_servers"],
            username=config["sasl_plain_username"],
            password=config["sasl_plain_password"],
            timeout=config.get("timeout", 10)
        )
        self.topics = topics

    def call_kafka(self, topic, batch_size=1):
        logger.debug("{}.Checking {}".format(self.__class__.__name__, topic))
        data = self.client.do_request(
            method="GET", params=dict(limit=batch_size),
            path="/topic/{}".format(topic)
        )
        for item in data:
            str_msg = item.get("Value", None)
            if str_msg:
                self.REGISTRY.run(str_msg)

    def run(self, loopinfo=None, batch_size=1):
        """ Run consumer
        """
        logger.info("{}.Starting...".format(self.__class__.__name__))
        if loopinfo:
            while True:
                for topic in self.topics:
                    self.call_kafka(topic, batch_size)
                time.sleep(loopinfo.sleep)
        else:
            for topic in self.topics:
                self.call_kafka(topic, batch_size)
