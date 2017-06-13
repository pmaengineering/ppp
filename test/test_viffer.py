#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for Viffer package."""
import unittest
from os import path as os_path
from pmix.viffer.__main__ import analyze
from pmix.viffer.error import VifferError


TEST_FORMS_DIRECTORY = os_path.dirname(os_path.realpath(__file__))


# pylint: disable=too-few-public-methods
# PyLint check not apply? - http://pylint-messages.wikidot.com/messages:r0903
class VifferTest:
    """Base class for Viffer package tests."""

    # TODO: Refactor this. Should use a different data structure, i.e. list.
    @staticmethod
    def get_forms(data):
        """Convert specified forms from name strings to objects."""
        # forms = {}
        # for datum in data:
        #     try:
        #         file = datum[0]['file']
        #     except KeyError:
        #         file = datum['inputs']['file']
        #     if file not in forms:
        #         # forms[file] = OdkForm(file=TEST_FORMS_DIRECTORY + '/' +
        #  file)
        #         pass
        # return forms
        pass


class VifferMainTest(unittest.TestCase, VifferTest):
    """Unit tests for the viffer.__main__."""

    def test_run(self):
        """Unit tests for the viffer.__main__.run()."""
        def test_run_args_xlsxfiles_error_raised():
            """Error is raised when incorrect number of files is passed."""
            cases = [
                ['Viffer-FQ-v1.xlsx'],
                ['Viffer-FQ-v1.xlsx', 'Viffer-FQ-v3.xlsx', 'Viffer-FQ-v3.xlsx']
            ]
            for case in cases:
                args = {'xlsxfiles': case}
                self.assertRaises(VifferError, analyze, args)

        test_run_args_xlsxfiles_error_raised()


if __name__ == '__main__':
    unittest.main()
