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


class OdkGroupToDictTest(unittest.TestCase):  # TODO: Add an actual test.
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


class OdkGroupRenderHeaderTest(unittest.TestCase):
    """Unit tests for the OdkGroup class"""
    def setUp(self):
        self.data = (
            ({'data': {'type': 'begin group', 'name': 'date_group', 'label::English': '', 'hint::English': '', 'constraint_message::English': '', 'constraint': '', 'required': '', 'appearance': 'field-list', 'default': '', 'relevant': 'today() > date("2017-03-01") and today() < date("2017-11-01")', 'read_only': '', 'calculation': '', 'choice_filter': '', 'image::English': '', 'save_instance': '', 'save_form': '', 'label::Ateso': '', 'label::Luganda': '', 'label::Lugbara': '', 'label::Luo': '', 'label::Lusoga': '', 'label::Ngakarimojong': '', 'label::Runyankole-Rukiga': '', 'label::Runyoro-Rutoro': '', 'hint::Ateso': '', 'hint::Luganda': '', 'hint::Lugbara': '', 'hint::Luo': '', 'hint::Lusoga': '', 'hint::Ngakarimojong': '', 'hint::Runyankole-Rukiga': '', 'hint::Runyoro-Rutoro': '', 'constraint_message::Ateso': '', 'constraint_message::Luganda': '', 'constraint_message::Lugbara': '', 'constraint_message::Luo': '', 'constraint_message::Lusoga': '', 'constraint_message::Ngakarimojong': '', 'constraint_message::Runyankole-Rukiga': '', 'constraint_message::Runyoro-Rutoro': '', 'label': '', 'hint': '', 'constraint_message': '', 'image': '', 'constraint_original': '', 'relevant_original': 'today() > date("2017-03-01") and today() < date("2017-11-01")', 'input_field': None}, 'lang': 'English', 'highlighting': False},
             type('<class \'str\'>')),
        )

    def test_render_header(self):
        for i, expected_output in self.data:
            output = type(OdkGroup(i).render_header(i['data'], i['lang'], i['highlighting']))
            msg = '\n\nCase:\n{}\nOutput:\n{}\nExpected:\n{}'.format(i, output, expected_output)
            self.assertTrue(output == expected_output, msg=msg)

if __name__ == '__main__':
    unittest.main()
