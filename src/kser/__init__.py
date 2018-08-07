#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import socket
import os

__hostname__ = socket.gethostname()

KSER_METRICS_ENABLED = os.getenv("KSER_METRICS_ENABLED", "no")
KSER_TASK_COUNT = None
KSER_TASKS_STATUS = None

if KSER_METRICS_ENABLED == "yes":
    from prometheus_client import Counter, Gauge

    KSER_TASK_COUNT = Gauge('kser_task_count', 'KSER tasks launched')
    KSER_TASKS_STATUS = Counter(
        'kser_task_result', 'KSER task status', ['hostname', 'name', 'status']
    )
