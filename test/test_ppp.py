#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Unit tests for ppp.py"""
import unittest
from os import path as os_path
from pmix.odkform import OdkForm
from pmix.odkprompt import OdkPrompt
# from pmix.odkchoices import OdkChoices
from pmix.odkgroup import OdkGroup
# from pmix.odkrepeat import OdkRepeat
# from pmix.odktable import OdkTable

test_forms_directory = os_path.dirname(os_path.realpath(__file__))


class PppTest:
    @staticmethod
    def get_forms(data):
        forms = {}
        for i, expected_output in data:
            if i['file'] not in forms:
                forms[i['file']] = OdkForm(f=test_forms_directory + '/' + i['file'])
        return forms


class OdkPromptTest(unittest.TestCase, PppTest):
    """Unit tests for the OdkPrompt class."""
    def setUp(self):
        self.data = (
            ({'file': 'FQ.xlsx', 'media_types': ['image', 'audio', 'video', 'media::image', 'media::audio',
                                                 'media::video']},
             {'lead_char': '[', 'end_char': ']'}),
        )

    def test_to_dict(self):
        def test_all_media_fields_in_all_prompts():
            arbitrary_language_param = 'English'
            forms = self.get_forms(self.data)
            for i, expected_output in self.data:
                lc = expected_output['lead_char']
                ec = expected_output['end_char']
                for item in forms[i['file']].questionnaire:
                    if isinstance(item, OdkPrompt):
                        d = item.to_dict(arbitrary_language_param)
                        for key, val in d.items():
                            for mt in i['media_types']:
                                if key.startswith(mt) and len(val) > 0:
                                    # A field such as 'media::image::English' is formatted correctly.
                                    self.assertTrue(val[0] == lc and val[-1] == ec)
                                    # A field such as 'image' exists and is formatted correctly.
                                    self.assertTrue(d[mt][0] == lc and d[mt][-1] == ec)
                                    # No discrepancies between language-based adn non-language based media fields.
                                    self.assertTrue(d[mt] == val)
                                    # The field 'media' exists and is formatted correctly.
                                    self.assertTrue(len(d['media']) > 0)
        test_all_media_fields_in_all_prompts()


class OdkGroupTest(unittest.TestCase):
    """Unit tests for the OdkGroup class."""
    def setUp(self):
        self.data = (
            ({'data': {'type': 'begin group', 'name': 'date_group', 'label::English': '', 'hint::English': '',
                       'constraint_message::English': '', 'constraint': '', 'required': '', 'appearance': 'field-list',
                       'default': '', 'relevant': 'today() > date("2017-03-01") and today() < date("2017-11-01")',
                       'read_only': '', 'calculation': '', 'choice_filter': '', 'image::English': '',
                       'save_instance': '', 'save_form': '', 'label::Ateso': '', 'label::Luganda': '',
                       'label::Lugbara': '', 'label::Luo': '', 'label::Lusoga': '', 'label::Ngakarimojong': '',
                       'label::Runyankole-Rukiga': '', 'label::Runyoro-Rutoro': '', 'hint::Ateso': '',
                       'hint::Luganda': '', 'hint::Lugbara': '', 'hint::Luo': '', 'hint::Lusoga': '',
                       'hint::Ngakarimojong': '', 'hint::Runyankole-Rukiga': '', 'hint::Runyoro-Rutoro': '',
                       'constraint_message::Ateso': '', 'constraint_message::Luganda': '',
                       'constraint_message::Lugbara': '', 'constraint_message::Luo': '',
                       'constraint_message::Lusoga': '', 'constraint_message::Ngakarimojong': '',
                       'constraint_message::Runyankole-Rukiga': '', 'constraint_message::Runyoro-Rutoro': '',
                       'label': '', 'hint': '', 'constraint_message': '', 'image': '', 'constraint_original': '',
                       'relevant_original': 'today() > date("2017-03-01") and today() < date("2017-11-01")',
                       'input_field': None
                       },
              'lang': 'English',
              'highlighting': False
              },
             type('<class \'str\'>')),
        )

    def test_render_header(self):
        for i, expected_output in self.data:
            output = type(OdkGroup(i).render_header(i['data'], i['lang'], i['highlighting']))
            msg = '\n\nCase:\n{}\nOutput:\n{}\nExpected:\n{}'.format(i, output, expected_output)
            self.assertTrue(output == expected_output, msg=msg)


class OdkFormQuestionnaireTest(unittest.TestCase, PppTest):
    """Unit tests for the OdkForm class."""
    def setUp(self):
        self.data = (
            ({'file': 'FQ.xlsx', 'position': 0},
             {'class': OdkGroup, 'repr': '<OdkGroup empty_warn_grp: [<OdkPrompt empty_form_warning>, '
                                         '<OdkPrompt ok_continue>]>'}),
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
             {'class': OdkGroup, 'repr': '<OdkGroup empty_warn_grp: [<OdkPrompt empty_form_warning>, '
                                         '<OdkPrompt ok_continue>]>'}),
            ({'file': 'FQ-nut.xlsx', 'position': 25},
             {'class': OdkGroup, 'repr': '<OdkGroup FQA: [<OdkPrompt age_warn>, <OdkPrompt age_diff>, '
                                         '<OdkPrompt age_same>, <OdkPrompt age>]>'}),
            ({'file': 'FQ-nut.xlsx', 'position': 50},
             {'class': OdkPrompt, 'repr': '<OdkPrompt nb_age>'}),
            ({'file': 'FQ-nut.xlsx', 'position': 75},
             {'class': OdkGroup, 'repr': '<OdkGroup ac_in_grp: [<OdkPrompt ac_iron_obtained>, '
                                         '<OdkPrompt ac_iron_tabs_img>]>'}),
            ({'file': 'FQ-nut.xlsx', 'position': 100},
             {'class': OdkPrompt, 'repr': '<OdkPrompt ar_book>'}),
        )

    def test_questionnaire(self):
        forms = self.get_forms(self.data)
        for i, expected_output in self.data:
            print(forms[i['file']].questionnaire)
            output = forms[i['file']].questionnaire[i['position']]
            self.assertTrue(str(output) == expected_output['repr'])
            self.assertTrue(isinstance(output, expected_output['class']))


if __name__ == '__main__':
    unittest.main()
