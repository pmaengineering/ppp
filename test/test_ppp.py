#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Unit tests for verbiage.py"""

# Unittest bad-ness:
# Consider package /pmix/pmix/test
# from /pmix, write python -m pmix.test.test_verbiage
# from /pmix, write python -m pmix.test (when I get a __main__.py)
# from /pmix, write python -m unittest # This is a shortcut for the next line
# from /pmix, write python -m unittest discover

# import os
# import sys
# print("PATH")
# print(*sys.path, sep='\n')
# print("CWD", os.getcwd())
# print("name", __name__)
# print("pacakge", __package__)

import unittest
# from pmix.odkform import OdkForm
# from pmix.odkprompt import OdkPrompt
# from pmix.odkchoices import Odkchoices
from pmix.odkgroup import OdkGroup
# from pmix.odkrepeat import OdkRepeat
# from pmix.odktable import OdkTable


class OdkGroupTest(unittest.TestCase):  # TODO: Add an actual test.
    """Unit tests for the OdkGroup class"""
    def setUp(self):
        self.data = (
            ('example_input', 'example_output'),
            ('example_input', 'example_output')
        )

    def test_to_dict(self):
        for i, expected_output in self.data:
            # output = OdkGroup(i).to_dict
            output = 'example_output'
            msg = '\n\nCase:\n{}\nExpected:\n{}'.format(i, expected_output)
            self.assertTrue(output == expected_output, msg=msg)

if __name__ == '__main__':
    unittest.main()
