#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import logging

from cdumay_error import ValidationError
from cdumay_result import Result, ResultSchema
from kser.schemas import Message
from kser.sequencing.task import Task

logger = logging.getLogger(__name__)


class Operation(Task):
    TASKS = ()

    def check_required_params(self):
        """ Check if all required parameters are set"""
        for param in self.REQUIRED_FIELDS:
            if param not in self.params:
                raise ValidationError("Missing parameter: {} for {}".format(
                    param, self.__class__.path
                ))

        for child in self.TASKS:
            for param in child.REQUIRED_FIELDS:
                if param not in self.params:
                    raise ValidationError(
                        "Missing parameter: {} for {}".format(param, child.path)
                    )

    @classmethod
    def new(cls, **kwargs):
        return cls(**cls.parse_inputs(**kwargs))

    @classmethod
    def parse_inputs(cls, **kwargs):
        return kwargs

    def __init__(self, uuid=None, status="PENDING", params=None, tasks=None,
                 result=None, metadata=None):
        Task.__init__(self, uuid=uuid, params=params, status=status,
                      result=result, metadata=metadata)
        self.tasks = tasks or list()

    def __repr__(self):
        return "Operation [{}](id={},status={})".format(
            self.__class__.__name__, self.uuid, self.status
        )

    def _set_status(self, status, result=None):
        """ update operation status

        :param str status: New status
        :param cdumay_result.Result result: Execution result
        """
        logger.info(
            "{}.SetStatus: {}[{}] status update '{}' -> '{}'".format(
                self.__class__.__name__, self.__class__.path, self.uuid,
                self.status, status
            ),
            extra=dict(
                kmsg=Message(
                    self.uuid, entrypoint=self.__class__.path,
                    params=self.params
                ).dump()
            )
        )
        return self.set_status(status, result)

    # noinspection PyUnusedLocal
    def set_status(self, status, result=None):
        """ update operation status

        :param str status: New status
        :param cdumay_result.Result result: Execution result
        """
        self.status = status

    def add_task(self, task):
        """ add task to operation

        :param kser.sequencing.task.Task task: task to add
        """
        self.tasks.append(task)

    def _prebuild(self, **kwargs):
        logger.debug(
            "{}.PreBuild: {}[{}]: {}".format(
                self.__class__.__name__, self.__class__.path, self.uuid, kwargs
            ),
            extra=dict(
                kmsg=Message(
                    self.uuid, entrypoint=self.__class__.path,
                    params=self.params
                ).dump()
            )
        )
        self.check_required_params()
        return self.prebuild(**kwargs)

    # noinspection PyMethodMayBeStatic
    def prebuild(self, **kwargs):
        """ to implement, perform check before the operation creation
        """
        return kwargs

    def _prerun(self):
        """ To execute before running message
        """
        self.check_required_params()
        self._set_status("RUNNING")
        logger.debug(
            "{}.PreRun: {}[{}]: running...".format(
                self.__class__.__name__, self.__class__.path, self.uuid
            ),
            extra=dict(
                kmsg=Message(
                    self.uuid, entrypoint=self.__class__.path,
                    params=self.params
                ).dump()
            )
        )
        return self.prerun()

    def _onsuccess(self, result):
        """ To execute on execution success
        :param cdumay_result.Result result: Execution result
        :return: Execution result
        :rtype: cdumay_result.Result
        """
        self._set_status("SUCCESS", result)
        logger.info(
            "{}.Success: {}[{}]: {}".format(
                self.__class__.__name__, self.__class__.path, self.uuid, result
            ),
            extra=dict(
                kmsg=Message(
                    self.uuid, entrypoint=self.__class__.path,
                    params=self.params
                ).dump(),
                kresult=ResultSchema().dump(result) if result else dict()
            )
        )
        return self.onsuccess(result)

    def _onerror(self, result):
        """ To execute on execution failure

        :param cdumay_result.Result result: Execution result
        :return: Execution result
        :rtype: cdumay_result.Result
        """
        self._set_status("FAILED", result)
        logger.error(
            "{}.Failed: {}[{}]: {}".format(
                self.__class__.__name__, self.__class__.path, self.uuid, result
            ),
            extra=dict(
                kmsg=Message(
                    self.uuid, entrypoint=self.__class__.path,
                    params=self.params
                ).dump(),
                kresult=ResultSchema().dump(result) if result else dict()
            )
        )
        return self.onerror(result)

    def unsafe_execute(self, result=None):
        self._prerun()
        for task in self.tasks:
            if task.status != 'SUCCESS':
                result = task.unsafe_execute(result=result)
                if result.retcode != 0:
                    return self._onerror(result)
            else:
                result = task.result

        return self._onsuccess(result=result)

    def display(self):
        """ dump operation

        """
        print("{}".format(self))
        for task in self.tasks:
            print("  - {}".format(task))

    def next(self, task):
        """ Find the next task

        :param kser.sequencing.task.Task task: previous task
        :return: The next task
        :rtype: kser.sequencing.task.Task or None
        """
        uuid = str(task.uuid)
        for idx, otask in enumerate(self.tasks[:-1]):
            if otask.uuid == uuid:
                if self.tasks[idx + 1].status != 'SUCCESS':
                    return self.tasks[idx + 1]
                else:
                    uuid = self.tasks[idx + 1].uuid

    def launch_next(self, task=None, result=None):
        """ Launch next task or finish operation

        :param kser.sequencing.task.Task task: previous task
        :param cdumay_result.Result result: previous task result

        :return: Execution result
        :rtype: cdumay_result.Result
        """
        if task:
            next_task = self.next(task)
            if next_task:
                return next_task.send(result=result)
            else:
                return self.set_status(task.status, result)
        elif len(self.tasks) > 0:
            return self.tasks[0].send(result=result)
        else:
            return Result(retcode=1, stderr="Nothing to do, empty operation !")

    def launch(self):
        """ Send the first task

        :return: Execution result
        :rtype: cdumay_result.Result
        """
        return self.launch_next()

    def finalize(self):
        """To implement, post build actions (database mapping ect...)

        :return: the controller
        :rtype: kser.sequencing.operation.Operation
        """
        return self

    def _build_tasks(self, **kwargs):
        """

        :param dict kwargs: tasks parameters (~=context)
        :return: list of tasks
        :rtype: list(kser.sequencing.operation.Operation)
        """
        tasks = self.build_tasks(**kwargs)
        logger.debug(
            "{}.BuildTasks: {} task(s) found".format(
                self.__class__.__name__, len(tasks)
            ),
            extra=dict(
                kmsg=Message(
                    self.uuid, entrypoint=self.__class__.path,
                    params=self.params
                ).dump()
            )
        )
        return tasks

    # noinspection PyMethodMayBeStatic
    # noinspection PyUnusedLocal
    def build_tasks(self, **kwargs):
        """ to implement

        :param dict kwargs: tasks parameters (~=context)
        :return: list of tasks
        :rtype: list(kser.sequencing.task.Task)
        """
        return list()

    def compute_tasks(self, **kwargs):
        """ perfrom checks and build tasks

        :return: list of tasks
        :rtype: list(kser.sequencing.operation.Operation)
        """
        params = self._prebuild(**kwargs)
        if not params:
            params = dict(kwargs)

        return self._build_tasks(**params)

    def build(self, **kwargs):
        """ create the operation and associate tasks

        :param dict kwargs: operation data
        :return: the controller
        :rtype: kser.sequencing.controller.OperationController
        """
        self.tasks += self.compute_tasks(**kwargs)
        return self.finalize()

    def send(self):
        """ Send operation to Kafka

        :return: The operation
        :rtype: kser.sequencing.operation.Operation
        """
