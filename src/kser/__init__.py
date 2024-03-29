#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import os
import socket

import pkg_resources

__version__ = pkg_resources.get_distribution('kser').version
__hostname__ = socket.gethostname()

# noinspection PyTypeChecker
os.environ.setdefault("LOCK_PATH", "/var/run")
# noinspection PyTypeChecker
os.environ.setdefault("RUNNING_FILE", os.path.join(
    os.environ['LOCK_PATH'], "kser-{}-run.lock".format(__hostname__)
))
# noinspection PyTypeChecker
os.environ.setdefault("LOCK_FILE", os.path.join(
    os.environ['LOCK_PATH'], "kser-{}-pause.lock".format(__hostname__)
))

KSER_METRICS_ENABLED = os.getenv("KSER_METRICS_ENABLED", "no")
KSER_TASK_COUNT = None
KSER_TASKS_STATUS = None

if KSER_METRICS_ENABLED == "yes":
    from prometheus_client import Counter, Gauge

    KSER_TASK_COUNT = Gauge('kser_task_count', 'KSER tasks launched')
    KSER_TASKS_STATUS = Counter(
        'kser_task_result', 'KSER task status', ['hostname', 'name', 'status']
    )
