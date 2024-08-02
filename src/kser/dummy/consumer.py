#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import logging
import os
import time
from pathlib import Path
from typing import Dict, List, NoReturn
from unittest.mock import Mock

from kser.controller import Controller

logger = logging.getLogger(__name__)


class Consumer:
    """Mother class for dummy consumer"""

    REGISTRY = Controller

    def __init__(self, config: Dict, topics: List[str]):
        self.client = Mock(config=config, topics=topics)
        self.clean_lock()

    def __del__(self):
        for lockfile in (os.environ["LOCK_FILE"], os.environ["RUNNING_FILE"]):
            path = Path(lockfile)
            if path.exists():
                logger.debug(f"Cleaning existing lock file: {lockfile}")
                path.unlink()

    @classmethod
    def clean_lock(cls):
        """Remove lock file"""
        path = Path(os.environ["LOCK_FILE"])
        if path.exists():
            logger.debug(f"Cleaning existing pause file {path}")
            path.unlink()

    @staticmethod
    def is_active() -> bool:
        """Is the lock file exists"""
        return not Path(os.environ["LOCK_FILE"]).exists()

    def run(self) -> NoReturn:
        """Run consumer"""
        logger.info("DummyConsumer.Starting...")

        while True:
            if self.is_active() is True:
                time.sleep(60)
                logger.debug("DummyConsumer: loop done.")
            else:
                logger.warning("DummyConsumer: Consumer is paused")
                time.sleep(60)
