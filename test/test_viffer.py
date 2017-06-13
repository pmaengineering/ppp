#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for Viffer package."""
from os import path as os_path, listdir
import unittest
import re
# from pmix.workbook import Workbook
from pmix.viffer.__main__ import render_form_objects
from pmix.viffer.error import VifferError


TEST_FORMS_DIRECTORY = os_path.dirname(os_path.realpath(__file__))


# pylint: disable=too-few-public-methods
# PyLint check not apply? - http://pylint-messages.wikidot.com/messages:r0903
class VifferTest:
    """Base class for Viffer package tests."""
    def __init__(self):
        self.test_forms = self.get_test_forms()
        self.test_ref_forms = self.get_test_ref_forms(self.test_forms)
    REF_FILE_NAME_PATTERN = r'[A-Za-z]{2}-ref-v?[0-9]{0,3}'  # Ex: FQ-ref-v13

    @staticmethod
    def get_test_forms():
        """Gets a list of all forms in test directory."""
        test_forms = []
        return test_forms

    @staticmethod
    def get_test_ref_forms(test_forms):
        """Gets a list of all forms in test directory matching ref pattern."""
        test_ref_forms = []
        return test_ref_forms

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

    def test_render_form_objects(self):
        """Unit tests for the viffer.__main__.run()."""

        def test_render_form_objects_args_xlsxfiles_error_raised():
            """Error is raised when incorrect number of files is passed."""
            cases = [
                ['Viffer-FQ-v1.xlsx'],
                ['Viffer-FQ-v1.xlsx', 'Viffer-FQ-v3.xlsx', 'Viffer-FQ-v3.xlsx']
            ]
            for case in cases:
                args = {'xlsxfiles': case}
                self.assertRaises(VifferError, render_form_objects, args)

        def test_render_form_objects_returns_wb_obj():
            """ODK form objects correctly created from ODK Xlsforms."""
            cases = ['']
            for case in cases:
                # TODO: Logic
                print(re.match(r'[A-Za-z]{2}-ref-[v0-9][0-9]{0,3}', 'FQ-ref-v13'))
                print(re.match(VifferTest.REF_FILE_NAME_PATTERN,
                               'FQ-ref-v13'))

                print(listdir(TEST_FORMS_DIRECTORY))
                self.assertTrue(True)
                # self.assertTrue(isinstance(case, Workbook))

        test_render_form_objects_args_xlsxfiles_error_raised()
        test_render_form_objects_returns_wb_obj()


if __name__ == '__main__':
    unittest.main()
