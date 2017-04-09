#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_mgtoolkit
----------------------------------

Tests for `mgtoolkit` module.
"""
import unittest
from tests.unit_tests import RunTests

suite = unittest.TestLoader().loadTestsFromTestCase(RunTests)
unittest.TextTestRunner(verbosity=2).run(suite)



