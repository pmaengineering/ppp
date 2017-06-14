#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for Viffer (Variable diff(erentiator)) package."""
from os import path as os_path, listdir
import unittest
import re
# from pmix.workbook import Workbook
from pmix.xlsform import Xlsform
from pmix.viffer.__main__ import render_form_objects
from pmix.viffer.error import VifferError


TEST_FORMS_DIRECTORY = os_path.dirname(os_path.realpath(__file__))


# pylint: disable=too-few-public-methods
# PyLint check not apply? - http://pylint-messages.wikidot.com/messages:r0903
class VifferTest:
    """Base class for Viffer package tests."""
    REF_FILE_NAME_PATTERN = r'[A-Za-z]{2}-ref-v?[0-9]{0,3}'  # Ex: FQ-ref-v13

    def __init__(self):
        self.test_forms = self.get_test_forms()
        self.test_ref_forms = self.get_test_ref_forms(self.test_forms)

    @staticmethod
    def get_test_forms():
        """Gets a list of all teset forms in test directory.

        Returns:
            list: Test forms.
        """
        xls_form_present = False
        test_forms = []
        for form in listdir(TEST_FORMS_DIRECTORY):
            if form.endswith('.xls'):
                xls_form_present = True
            elif form.endswith('.xlsx'):
                test_forms.append(form)
        if xls_form_present:
            print('WARNING: File(s) with \'.xls\' extension found in test '
                  'directory \'{}\'. XlsForms of \'.xls\' extension have been '
                  'deprecated according to PMA2020 ODK standards. It is '
                  'recommended to use \'.xlsx\'.'.format(TEST_FORMS_DIRECTORY))
        return test_forms

    @staticmethod
    def get_test_ref_forms(test_forms):
        """Gets a list of all forms in test directory matching ref pattern.

        Args:
            test_forms (list): A list of test forms.

        Returns:
            list: Reference template test forms.
        """
        test_ref_forms = []
        for form in test_forms:
            if re.match(VifferTest.REF_FILE_NAME_PATTERN, form):
                test_ref_forms.append(form)
        return test_ref_forms


class VifferMainTest(unittest.TestCase, VifferTest):
    """Unit tests for the viffer.__main__."""
    def __init__(self, *args, **kwargs):
        super(VifferMainTest, self).__init__(*args, **kwargs)
        VifferTest.__init__(self)

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
            for form in self.test_ref_forms:  # TODO: Use the __main__.py
                # function, not the instance attribute.
                file = TEST_FORMS_DIRECTORY + '/' + form
                self.assertTrue(isinstance(Xlsform(file), Xlsform))

        test_render_form_objects_args_xlsxfiles_error_raised()
        test_render_form_objects_returns_wb_obj()


if __name__ == '__main__':
    unittest.main()
