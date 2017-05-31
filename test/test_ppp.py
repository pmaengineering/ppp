#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Unit tests for verbiage.py"""

# Unittest bad-ness:
# Consider package /pmix/pmix/test
# from /pmiOdkPrompt, write python -m pmix.test.test_verbiage
# from /pmiOdkPrompt, write python -m pmix.test (when I get a __main__.py)
# from /pmiOdkPrompt, write python -m unittest # This is a shortcut for the next line
# from /pmiOdkPrompt, write python -m unittest discover

# import os
# import sys
# print("PATH")
# print(*sys.path, sep='\n')
# print("CWD", os.getcwd())
# print("name", __name__)
# print("pacakge", __package__)

import unittest
from os import path as os_path
from pmix.odkform import OdkForm
from pmix.odkprompt import OdkPrompt
# from pmix.odkchoices import Odkchoices
from pmix.odkgroup import OdkGroup
# from pmix.odkrepeat import OdkRepeat
# from pmix.odktable import OdkTable

test_forms_directory = os_path.dirname(os_path.realpath(__file__))


class OdkGroupToDictTest(unittest.TestCase):  # TODO: Add an actual test.
    """Unit tests for the OdkGroup to_dict method."""
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
    """Unit tests for the OdkGroup render_header method."""
    def setUp(self):
        self.data = (
            ({'data': {'type': 'begin group', 'repr': 'date_group', 'label::English': '', 'hint::English': '', 'constraint_message::English': '', 'constraint': '', 'required': '', 'appearance': 'field-list', 'default': '', 'relevant': 'today() > date("2017-03-01") and today() < date("2017-11-01")', 'read_only': '', 'calculation': '', 'choice_filter': '', 'image::English': '', 'save_instance': '', 'save_form': '', 'label::Ateso': '', 'label::Luganda': '', 'label::Lugbara': '', 'label::Luo': '', 'label::Lusoga': '', 'label::Ngakarimojong': '', 'label::Runyankole-Rukiga': '', 'label::Runyoro-Rutoro': '', 'hint::Ateso': '', 'hint::Luganda': '', 'hint::Lugbara': '', 'hint::Luo': '', 'hint::Lusoga': '', 'hint::Ngakarimojong': '', 'hint::Runyankole-Rukiga': '', 'hint::Runyoro-Rutoro': '', 'constraint_message::Ateso': '', 'constraint_message::Luganda': '', 'constraint_message::Lugbara': '', 'constraint_message::Luo': '', 'constraint_message::Lusoga': '', 'constraint_message::Ngakarimojong': '', 'constraint_message::Runyankole-Rukiga': '', 'constraint_message::Runyoro-Rutoro': '', 'label': '', 'hint': '', 'constraint_message': '', 'image': '', 'constraint_original': '', 'relevant_original': 'today() > date("2017-03-01") and today() < date("2017-11-01")', 'input_field': None}, 'lang': 'English', 'highlighting': False},
             type('<class \'str\'>')),
        )

    def test_render_header(self):
        for i, expected_output in self.data:
            output = type(OdkGroup(i).render_header(i['data'], i['lang'], i['highlighting']))
            msg = '\n\nCase:\n{}\nOutput:\n{}\nExpected:\n{}'.format(i, output, expected_output)
            self.assertTrue(output == expected_output, msg=msg)


class OdkFormQuestionnaireTest(unittest.TestCase):
    """Unit tests for the OdkGroup render_header method."""
    def setUp(self):
        self.data = (
            ({'file': 'FQ.xlsx', 'position': 0},
             {'class': OdkGroup, 'repr': '<OdkGroup empty_warn_grp: [<OdkPrompt empty_form_warning>, <OdkPrompt ok_continue>]>'}),
            ({'file': 'FQ.xlsx', 'position': 25},
             {'class': OdkPrompt, 'repr': '<OdkPrompt school>'}),
            ({'file': 'FQ.xlsx', 'position': 50},
             {'class': OdkPrompt, 'repr': '<OdkPrompt children_died_error>'}),
            ({'file': 'FQ.xlsx', 'position': 75},
             {'class': OdkPrompt, 'repr': '<OdkPrompt more_children_pregnant>'}),
            ({'file': 'FQ.xlsx', 'position': 100},
             {'class': OdkPrompt, 'repr': '<OdkPrompt injectable_probe_current>'}),
            ({'file': 'HQ.xlsx', 'position': 0},
             {'class': OdkPrompt, 'repr': '<OdkPrompt your_name_check>'}),
            ({'file': 'HQ.xlsx', 'position': 25},
             {'class': OdkPrompt, 'repr': '<OdkPrompt error_extraheads>'}),
            ({'file': 'HQ.xlsx', 'position': 50},
             {'class': OdkPrompt, 'repr': '<OdkPrompt water_months_avail_2>'}),
            ({'file': 'HQ.xlsx', 'position': 75},
             {'class': OdkPrompt, 'repr': '<OdkPrompt water_reliability_8>'}),
            ({'file': 'HQ.xlsx', 'position': 100},
             {'class': OdkPrompt, 'repr': '<OdkPrompt water_collection_14>'}),
            ({'file': 'SQ.xlsx', 'position': 0},
             {'class': OdkPrompt, 'repr': '<OdkPrompt your_name_check>'}),
            ({'file': 'SQ.xlsx', 'position': 25},
             {'class': OdkPrompt, 'repr': '<OdkPrompt sect_services_info>'}),
            ({'file': 'SQ.xlsx', 'position': 50},
             {'class': OdkPrompt, 'repr': '<OdkPrompt fp_offered>'}),
            ({'file': 'SQ.xlsx', 'position': 75},
             {'class': OdkPrompt, 'repr': '<OdkPrompt implant_insert>'}),
            ({'file': 'SQ.xlsx', 'position': 100},
             {'class': OdkPrompt, 'repr': '<OdkPrompt stock_implants>'}),
            ({'file': 'FQ-nut.xlsx', 'position': 0},
             {'class': OdkGroup, 'repr': '<OdkGroup empty_warn_grp: [<OdkPrompt empty_form_warning>, <OdkPrompt ok_continue>]>'}),
            ({'file': 'FQ-nut.xlsx', 'position': 25},
             {'class': OdkGroup, 'repr': '<OdkGroup FQA: [<OdkPrompt age_warn>, <OdkPrompt age_diff>, <OdkPrompt age_same>, <OdkPrompt age>]>'}),
            ({'file': 'FQ-nut.xlsx', 'position': 50},
             {'class': OdkPrompt, 'repr': '<OdkPrompt nb_age>'}),
            ({'file': 'FQ-nut.xlsx', 'position': 75},
             {'class': OdkGroup, 'repr': '<OdkGroup ac_in_grp: [<OdkPrompt ac_iron_obtained>, <OdkPrompt ac_iron_tabs_img>]>'}),
            ({'file': 'FQ-nut.xlsx', 'position': 100},
             {'class': OdkPrompt, 'repr': '<OdkPrompt ar_book>'}),
        )

    def test_questionnaire(self):
        forms = {}
        for i, expected_output in self.data:
            #
            if i['file'] not in forms:
                forms[i['file']] = OdkForm(f=test_forms_directory + '/' + i['file'])
            output = forms[i['file']].questionnaire[i['position']]
            self.assertTrue(str(output) == expected_output['repr'])
            self.assertTrue(isinstance(output, expected_output['class']))


if __name__ == '__main__':
    unittest.main()
