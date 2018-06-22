#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for PPP package."""
import unittest
import os
import subprocess
from glob import glob

from ppp.odkform import OdkForm
from ppp.odkprompt import OdkPrompt
from ppp.odkgroup import OdkGroup
from test.config import TEST_FILES_DIR, TEST_PACKAGES
from test.utils import get_args, get_test_suite
# from pmix.odkchoices import OdkChoices  # TODO
# from pmix.odkrepeat import OdkRepeat  # TODO
# from pmix.odktable import OdkTable  # TODO


# # Mock Objects
class MockForm(OdkForm):
    """Mock object of OdkForm"""

    def __init__(self, mock_file, mock_dir=None):
        """Initialize mock form.

        Args:
            mock_file (str): File name.
            mock_dir (str): Directory.
        """
        path = mock_dir + mock_file if mock_dir else TEST_FILES_DIR + mock_file
        form = super().from_file(path)
        super().__init__(form)


# # Unit Tests
# pylint: disable=too-few-public-methods
# - PyLint check not apply? - http://pylint-messages.wikidot.com/messages:r0903
class PppTest(unittest.TestCase):
    """Base class for PPP package tests."""

    @classmethod
    def files_dir(cls):
        """Return name of test class."""
        return TEST_FILES_DIR + cls.__name__

    def input_path(self):
        """Return path of input file folder for test class."""
        return self.files_dir() + '/input/'

    def output_path(self):
        """Return path of output file folder for test class."""
        return self.files_dir() + '/output/'

    def input_files(self):
        """Return paths of input files for test class."""
        all_files = glob(self.input_path() + '*')
        # With sans_temp_files, you can have XlsForms open while testing.
        sans_temp_files = [x for x in all_files
                           if not x[len(self.input_path()):].startswith('~$')]
        return sans_temp_files

    def output_files(self):
        """Return paths of input files for test class."""
        return glob(self.output_path() + '*')

    def standard_convert(self):
        """Converts input/* --> output/*. Returns n files each."""
        in_files = self.input_files()
        out_dir = self.output_path()

        subprocess.call(['rm', '-rf', out_dir])
        os.makedirs(out_dir)
        command = ['python', '-m', 'ppp'] + in_files + ['-o', out_dir]
        subprocess.call(command)

        expected = 'N files: ' + str(len(in_files))
        actual = 'N files: ' + str(len(self.output_files()))
        return expected, actual

    def standard_conversion_test(self):
        """Checks standard convert success."""
        expected, actual = self.standard_convert()
        self.assertEqual(expected, actual)

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
                forms[file] = OdkForm.from_file(TEST_FILES_DIR + file)
        return forms


class OdkPromptTest(PppTest):
    """Unit tests for the OdkPrompt class."""

    media_types = ['image', 'audio', 'video', 'media::image',
                   'media::audio', 'media::video']
    media_lead_char = '['
    media_end_char = ']'
    arbitrary_language_param = 'English'

    def setUp(self):
        """Set up."""
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
            def asserts(item_dict):
                """Iterate through asserts."""
                for key, val in item_dict.items():
                    for media_type in OdkPromptTest.media_types:
                        if key.startswith(media_type) and val:
                            # A field such as 'media::image::English'
                            # is formatted correctly.
                            self.assertTrue(val[0] == lead_char and
                                            val[-1] == end_char)
                            # A field such as 'image' exists and is
                            # formatted correctly.
                            self.assertTrue(
                                item_dict[media_type][0] == lead_char and
                                item_dict[media_type][-1] == end_char)
                            # No discrepancies between language based and non
                            # language based media fields.
                            self.assertTrue(item_dict[media_type] == val)
                            # The field 'media' exists and formatted correct.
                            self.assertTrue(item_dict['media'])
            lang = OdkPromptTest.arbitrary_language_param
            lead_char = OdkPromptTest.media_lead_char
            end_char = OdkPromptTest.media_end_char
            forms = self.get_forms(self.data)
            for i in self.data:
                file_name = i['inputs']['file']
                for item in forms[file_name].questionnaire:
                    if isinstance(item, OdkPrompt):
                        asserts(item.to_dict(lang))

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
        """Set up."""
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


class OdkFormTest(PppTest):
    """Unit tests for the OdkForm class."""

    def setUp(self):
        """Set up."""
        self.data = (
            {'inputs': {'file': 'OdkFormTest.xlsx'}, 'position': 0,
             'outputs': {'class': OdkPrompt,
                         'repr': '<OdkPrompt ever_birth>'}},
            {'inputs': {'file': 'OdkFormTest.xlsx'}, 'position': 1,
             'outputs': {'class': OdkGroup,
                         'repr': '<OdkGroup FB: [<OdkPrompt fb_note>, '
                                 '<OdkPrompt fb_m>, <OdkPrompt fb_y>]>'}},
            {'inputs': {'file': 'OdkFormTest.xlsx'}, 'position': 2,
             'outputs': {'class': OdkPrompt,
                         'repr': '<OdkPrompt birth_events_yes>'}},
            {'inputs': {'file': 'OdkFormTest.xlsx'}, 'position': 3,
             'outputs': {'class': OdkPrompt,
                         'repr': '<OdkPrompt children_living>'}},
        )

    def test_questionnaire(self):
        """Test expected results of converted questionnaire based on position.
        """
        forms = self.get_forms(self.data)

        for datum in self.data:
            expected_output = datum['outputs']
            output = \
                forms[datum['inputs']['file']].questionnaire[datum['position']]

            # - Check Object Representation
            got = str(output)
            expected = expected_output['repr']
            msg = '\nGot: {}\nExpected: {}'.format(got, expected)
            self.assertEqual(got, expected, msg)

            # - Check Object Class
            got = output
            expected = expected_output['class']
            msg = '\nGot: {}\nExpected: {}'.format(got, expected)
            # noinspection PyTypeChecker
            self.assertTrue(isinstance(got, expected), msg)

    def test_to_html(self):
        """Test to_html method."""
        forms = self.get_forms(self.data)
        for dummy, form in forms.items():
            kwargs = {'format': 'html'}
            html = form.to_html(**kwargs)
            self.assertTrue(html.startswith("""<html>\n    <head>"""))
            self.assertTrue(html.endswith('</html>'))
            self.assertIn("""    </head>\n    <body id="survey">
        <div id="container">
            <div id="identification_section" class="section">""", html)


class MultiConversionTest(unittest.TestCase):
    """Test conversion of n files in n languages for n option combinations."""

    def test_multi_conversion(self):
        src_dir = TEST_FILES_DIR + 'multiple_file_language_option_conversion/'
        out_dir = src_dir + 'ignored/'
        src_dir_ls_input = os.listdir(src_dir)
        src_files = \
            [src_dir + x for x in src_dir_ls_input if x.endswith('.xlsx')]
        subprocess.call(['rm', '-rf', out_dir])
        os.makedirs(out_dir)
        command = ['python', '-m', 'ppp'] + src_files + \
                  ['-o', out_dir, '-f', 'doc', 'html', '-p', 'minimal', 'full',
                   '-l', 'English', 'Français']
        subprocess.call(command)

        out_dir_ls_input = str(os.listdir(out_dir))
        expected_output = \
            str(['BFR5-Selection-v2-jef-Français-minimal.html',
                 'BFR5-Female-Questionnaire-v13-jef-Français-full.html',
                 'BFR5-Female-Questionnaire-v13-jef-English-minimal.doc',
                 'BFR5-Female-Questionnaire-v13-jef-Français-full.doc',
                 'BFR5-Selection-v2-jef-Français-full.html',
                 'BFR5-Female-Questionnaire-v13-jef-English-full.doc',
                 'BFR5-Female-Questionnaire-v13-jef-Français-minimal.html',
                 'BFR5-Selection-v2-jef-Français-full.doc',
                 'BFR5-Female-Questionnaire-v13-jef-Français-minimal.doc',
                 'BFR5-Female-Questionnaire-v13-jef-English-full.html',
                 'BFR5-Selection-v2-jef-English-minimal.doc',
                 'BFR5-Selection-v2-jef-English-minimal.html',
                 'BFR5-Female-Questionnaire-v13-jef-English-minimal.html',
                 'BFR5-Selection-v2-jef-Français-minimal.doc',
                 'BFR5-Selection-v2-jef-English-full.doc',
                 'BFR5-Selection-v2-jef-English-full.html'])
        self.assertEqual(expected_output, str(out_dir_ls_input))


class MultipleFieldLanguageDelimiterSupport(PppTest):
    """Support for both : and :: to be used as delimiter betw field & lang.

        This test checks conversion for the ':' delimiter, specifically, which
        is occasionally used in some XlsForm specs, such as SurveyCTO. The '::'
        delimiter case is already covered by other tests since they use
        mostly vanilla ODK XlsForms using the '::' delimiter.
    """

    def test_convert(self):
        self.standard_conversion_test()


class SkipPatternColRelevantOrRelevance(PppTest):
    """Allow [relevant || relevance]"""

    def test_convert(self):
        self.standard_conversion_test()


class ChoiceColNameOrValue(PppTest):
    """Allow choices worksheet col [name || value]"""

    def test_convert(self):
        self.standard_conversion_test()


class SpacesInFileName(PppTest):
    """Spaces in file name: Replace or allow"""

    def test_convert(self):
        self.standard_conversion_test()


class SurveyCtoSupport(PppTest):
    """Check for successful conversion of an actual SurveyCtoFile"""

    def test_convert(self):
        self.standard_conversion_test()


if __name__ == '__main__':
    PARAMS = get_args()
    TEST_SUITE = get_test_suite(TEST_PACKAGES)
    unittest.TextTestRunner(verbosity=1).run(TEST_SUITE)

    if not PARAMS.doctests_only:
        unittest.main()
