#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""

import unittest

import pkg_resources


class InstallTest(unittest.TestCase):
    """Test install"""

    def test_install(self):
        """Test module is installed"""
        self.assertIn('kser', [x.key for x in pkg_resources.working_set])
