#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import logging
from typing import List, Optional
from unittest.mock import Mock

from cdumay_result import Result
from kser.controller import BaseProducer
from kser.schemas import Message

logger = logging.getLogger(__name__)


class Producer(BaseProducer):
    """Mother class for producers"""

    def __init__(self, config):
        """Create new Producer instance using provided configuration dict."""
        self.client = Mock(config=config)

    def bulk_send(
        self, topic: str, kmsgs: List[Message], timeout: Optional[int] = 60
    ) -> Result:
        """Send a batch of messages"""
        for kmsg in kmsgs:
            self._onmessage(kmsg).dumps().encode("UTF-8")
        return Result(
            stdout=f"{len(kmsgs)} message(s) sent to {topic} "
            f"(timeout: {timeout})"
        )

    # noinspection PyUnusedLocal
    def _send(
        self, topic: str, kmsg: Message, timeout: Optional[int] = 60
    ) -> Result:
        """Send the message into the given topic"""
        self._onmessage(kmsg).dumps().encode("UTF-8")
        return self._onsuccess(
            kmsg=kmsg,
            result=Result(
                uuid=kmsg.uuid,
                stdout=f"Message {kmsg.entrypoint}[{kmsg.uuid}] sent "
                f"in {topic} (timeout: {timeout})",
            ),
        )
