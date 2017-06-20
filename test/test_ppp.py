#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for PPP package."""
import unittest
import doctest
import os
from argparse import ArgumentParser
from pmix.ppp.odkform import OdkForm
from pmix.ppp.odkprompt import OdkPrompt
from pmix.ppp.odkgroup import OdkGroup
# from pmix.odkchoices import OdkChoices
# from pmix.odkrepeat import OdkRepeat
# from pmix.odktable import OdkTable

TEST_PACKAGE = 'pmix.ppp'
TEST_FORMS_DIRECTORY = os.path.dirname(os.path.realpath(__file__)) + '/files'


# pylint: disable=too-few-public-methods
# PyLint check not apply? - http://pylint-messages.wikidot.com/messages:r0903
class PppTest:
    """Base class for PPP package tests."""

    @staticmethod
    def get_forms(data):
        """Convert specified forms from form name strings to objects."""
        forms = {}
        for datum in data:
            # Should streamline setUps. Currently in both tuple and dict.
            try:
                file = datum[0]['file']
            except KeyError:
                file = datum['inputs']['file']
            if file not in forms:
                forms[file] = OdkForm(file=TEST_FORMS_DIRECTORY + '/' + file)
        return forms


class OdkPromptTest(unittest.TestCase, PppTest):
    """Unit tests for the OdkPrompt class."""

    media_types = ['image', 'audio', 'video', 'media::image',
                   'media::audio', 'media::video']
    media_lead_char = '['
    media_end_char = ']'
    arbitrary_language_param = 'English'

    def setUp(self):
        self.data = (
            ({'inputs': {
                'file': 'FQ.xlsx'
            }, 'expected_outputs': {

            }},
             {'inputs': {
                 'file': 'HQ.xlsx'
             }, 'expected_outputs': {

             }},
            )
        )

    def test_to_dict(self):
        """Test to_dict method."""
        def test_media_fields_in_prompts():
            """Tests for media fields."""
            lang = OdkPromptTest.arbitrary_language_param
            lead_char = OdkPromptTest.media_lead_char
            end_char = OdkPromptTest.media_end_char
            forms = self.get_forms(self.data)
            for i in self.data:
                file_name = i['inputs']['file']
                for item in forms[file_name].questionnaire:
                    if isinstance(item, OdkPrompt):
                        item_dict = item.to_dict(lang)
                        for key, val in item_dict.items():
                            for media_type in OdkPromptTest.media_types:
                                if key.startswith(media_type) and len(val) > 0:
                                    # A field such as 'media::image::English'
                                    # is formatted correctly.
                                    self.assertTrue(val[0] == lead_char and
                                                    val[-1] == end_char)
                                    # A field such as 'image' exists and is
                                    # formatted correctly.
                                    self.assertTrue(
                                        item_dict[media_type][0] == lead_char
                                        and
                                        item_dict[media_type][-1] == end_char)
                                    # No discrepancies between language
                                    # based and non-language based media
                                    # fields.
                                    self.assertTrue(
                                        item_dict[media_type] == val)
                                    # The field 'media' exists and is
                                    # formatted correctly.
                                    self.assertTrue(
                                        len(item_dict['media']) > 0)
        test_media_fields_in_prompts()

    def test_initialization_has_choices(self):
        """Test that choice list exists on initialization."""
        forms = self.get_forms(self.data)
        for dummy, form in forms.items():
            for item in form.questionnaire:
                if isinstance(item, OdkPrompt):
                    if item.odktype in item.select_types:
                        msg = 'No choices found in \'{}\'.'.format(item)
                        self.assertTrue(item.choices is not None, msg=msg)


class OdkGroupTest(unittest.TestCase):
    """Unit tests for the OdkGroup class."""

    def setUp(self):
        self.data = (
            ({'inputs': {'type': 'begin group', 'name': 'date_group',
                         'label::English': '', 'hint::English': '',
                         'constraint_message::English': '', 'constraint': '',
                         'required': '', 'appearance': 'field-list',
                         'default': '',
                         'relevant': 'today() > date("2017-03-01") and '
                                     'today() < date("2017-11-01")',
                         'read_only': '', 'calculation': '', 'choice_filter':
                             '', 'image::English': '',
                         'save_instance': '', 'save_form': '', 'label::Ateso':
                             '', 'label::Luganda': '',
                         'label::Lugbara': '', 'label::Luo': '',
                         'label::Lusoga': '', 'label::Ngakarimojong': '',
                         'label::Runyankole-Rukiga': '',
                         'label::Runyoro-Rutoro': '', 'hint::Ateso': '',
                         'hint::Luganda': '', 'hint::Lugbara': '', 'hint::Luo':
                             '', 'hint::Lusoga': '',
                         'hint::Ngakarimojong': '', 'hint::Runyankole-Rukiga':
                             '', 'hint::Runyoro-Rutoro': '',
                         'constraint_message::Ateso': '',
                         'constraint_message::Luganda': '',
                         'constraint_message::Lugbara': '',
                         'constraint_message::Luo': '',
                         'constraint_message::Lusoga': '',
                         'constraint_message::Ngakarimojong': '',
                         'constraint_message::Runyankole-Rukiga': '',
                         'constraint_message::Runyoro-Rutoro': '',
                         'label': '', 'hint': '', 'constraint_message': '',
                         'image': '', 'constraint_original': '',
                         'relevant_original': 'today() > date("2017-03-01") '
                                              'and today() < date("2017-11-01"'
                                              ')',
                         'input_field': None},
              'outputs': {
                  'header_primitive_type': type({})
              }}),
        )

    def test_render_header(self):
        """Test header rendering."""
        for i in self.data:
            expected_output = i['outputs']['header_primitive_type']
            output = type(OdkGroup(i['inputs']).format_header(i['inputs']))
            msg = '\n\nCase:\n{}\nOutput:\n{}\nExpected:\n{}'\
                .format(i, output, expected_output)
            self.assertTrue(output == expected_output, msg=msg)


class OdkFormTest(unittest.TestCase, PppTest):
    """Unit tests for the OdkForm class."""

    def setUp(self):
        self.data = (
            ({'file': 'FQ.xlsx', 'position': 0},
             {'class': OdkGroup,
              'repr': '<OdkGroup empty_warn_grp: '
                      '[<OdkPrompt empty_form_warning>, '
                      '<OdkPrompt ok_continue>]>'}),
            ({'file': 'FQ.xlsx', 'position': 25},
             {'class': OdkPrompt, 'repr': '<OdkPrompt school>'}),
            ({'file': 'FQ.xlsx', 'position': 50},
             {'class': OdkPrompt, 'repr': '<OdkPrompt children_died_error>'}),
            ({'file': 'FQ.xlsx', 'position': 75},
             {'class': OdkPrompt,
              'repr': '<OdkPrompt more_children_pregnant>'}),
            ({'file': 'FQ.xlsx', 'position': 100},
             {'class': OdkPrompt,
              'repr': '<OdkPrompt injectable_probe_current>'}),
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
             {'class': OdkGroup,
              'repr': '<OdkGroup empty_warn_grp: [<OdkPrompt '
                      'empty_form_warning>, <OdkPrompt ok_continue>]>'}),
            ({'file': 'FQ-nut.xlsx', 'position': 25},
             {'class': OdkGroup,
              'repr': '<OdkGroup FQA: [<OdkPrompt age_warn>, <OdkPrompt '
                      'age_diff>, <OdkPrompt age_same>, <OdkPrompt age>]>'}),
            ({'file': 'FQ-nut.xlsx', 'position': 50},
             {'class': OdkPrompt, 'repr': '<OdkPrompt nb_age_youngest>'}),
            ({'file': 'FQ-nut.xlsx', 'position': 75},
             {'class': OdkPrompt, 'repr': '<OdkPrompt ac_bp_check>'}),
            ({'file': 'FQ-nut.xlsx', 'position': 100},
             {'class': OdkPrompt, 'repr': '<OdkPrompt over_2yr_warning>'}),
        )

    def test_questionnaire(self):
        """Test expected results of converted questionnaire based on
        position."""
        forms = self.get_forms(self.data)
        for i, expected_output in self.data:
            output = forms[i['file']].questionnaire[i['position']]
            self.assertTrue(str(output) == expected_output['repr'])
            self.assertTrue(isinstance(output, expected_output['class']))

    def test_languages(self):
        """Language based tests."""
        def test_get_label_language_list():
            """Test OdkForm.get_label_language_list()."""
            test_input = {
                'audio': {
                    'has_generic_language_field': True,
                    'language_list': []
                },
                'constraint_message': {
                    'has_generic_language_field': False,
                    'language_list': ['Ateso', 'English', 'Luganda',
                                      'Lugbara', 'Luo', 'Lusoga',
                                      'Ngakarimojong', 'Runyankole-Rukiga',
                                      'Runyoro-Rutoro']
                },
                'hint': {
                    'has_generic_language_field': False,
                    'language_list': ['Ateso', 'English', 'Luganda',
                                      'Lugbara', 'Luo', 'Lusoga',
                                      'Ngakarimojong', 'Runyankole-Rukiga',
                                      'Runyoro-Rutoro']
                },
                'image': {
                    'has_generic_language_field': False,
                    'language_list': ['Ateso', 'English', 'Luganda',
                                      'Lugbara', 'Luo', 'Lusoga',
                                      'Ngakarimojong', 'Runyankole-Rukiga',
                                      'Runyoro-Rutoro']
                },
                'label': {
                    'has_generic_language_field': False,
                    'language_list': ['Ateso', 'English', 'Luganda',
                                      'Lugbara', 'Luo', 'Lusoga',
                                      'Ngakarimojong', 'Runyankole-Rukiga',
                                      'Runyoro-Rutoro']
                },
                'media::video': {
                    'has_generic_language_field': False,
                    'language_list': ['English']
                }
            }
            expected_output = ['Ateso', 'English', 'Luganda', 'Lugbara', 'Luo',
                               'Lusoga', 'Ngakarimojong', 'Runyankole-Rukiga',
                               'Runyoro-Rutoro']
            self.assertTrue(
                OdkForm.get_label_language_list(test_input) == expected_output)
        test_get_label_language_list()


if __name__ == '__main__':
    def get_args():
        """CLI for PPP test runner."""
        desc = 'Run tests for PPP package.'
        parser = ArgumentParser(description=desc)
        doctests_only_help = 'Specifies whether to run doctests only, as ' \
                             'opposed to doctests with unittests. Default is' \
                             ' False.'
        parser.add_argument('-d', '--doctests-only', action='store_true',
                            help=doctests_only_help)
        args = parser.parse_args()
        return args

    def get_test_modules(test_package):
        """Get files to test.

        Args:
            test_package (str): The package containing modules to test.

        Returns:
            list: List of all python modules in package.
        """
        test_modules = []
        root_dir = TEST_FORMS_DIRECTORY + "/../../" + "pmix/ppp"

        for dummy, dummy, filenames in os.walk(root_dir):
            for file in filenames:
                if file.endswith('.py'):
                    file = file[:-3]
                    test_module = test_package + '.' + file
                    test_modules.append(test_module)
        return test_modules

    def get_test_suite():
        """Get suite to test.

        Returns:
            TestSuite: Suite to test.
        """
        suite = unittest.TestSuite()
        pkg_modules = get_test_modules(test_package=TEST_PACKAGE)
        for pkg_module in pkg_modules:
            suite.addTest(doctest.DocTestSuite(pkg_module))
        return suite

    PARAMS = get_args()
    TEST_SUITE = get_test_suite()
    unittest.TextTestRunner(verbosity=1).run(TEST_SUITE)
    if PARAMS.doctests_only:
        pass
        # TEST_SUITE = get_test_suite()
        # unittest.TextTestRunner(verbosity=1).run(TEST_SUITE)
    else:
        # unittest.main()
        pass
