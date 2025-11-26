#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""

import unittest

from importlib.metadata import distributions


class InstallTest(unittest.TestCase):
    """Test install"""

    def test_install(self):
        """Test module is installed"""
        self.assertIn("kser", [x.name for x in distributions()])
