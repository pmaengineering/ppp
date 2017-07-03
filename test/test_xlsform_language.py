"""Tests for Xlsform module."""
import os.path
import unittest
from pmix.xlsform import Xlsform


class XlsFormLanguageTest(unittest.TestCase):
    """Unit tests for testing form languages in Xlsform and Xlstab."""

    FORM_DIR = 'test/files'

    def test_form_language(self):
        """Form language is correctly determined."""
        answers = (('language-default-none.xlsx', None),
                   ('language-missing-default.xlsx', 'Dioula'),
                   ('language-settings-default.xlsx', 'French'))

        for path, language in answers:
            form_path = os.path.join(self.FORM_DIR, path)
            xlsform = Xlsform(form_path)
            found = xlsform.form_language
            msg = 'Working with "{}"'.format(path)
            self.assertEqual(language, found, msg=msg)

    def test_sheet_language(self):
        """Languages found in a sheet are correctly determined."""
        answers = (
            ('language-default-none.xlsx', {
                'survey': [None, 'Dioula', 'English', 'French', 'Fulfulde',
                           'Gourmantchema', 'Moore'],
                'choices': ['English', 'French'],
                'settings': []
            }),
        )

        for path, answer in answers:
            form_path = os.path.join(self.FORM_DIR, path)
            xlsform = Xlsform(form_path)
            for sheet in xlsform:
                found = sheet.sheet_languages()
                name = sheet.name
                expected = answer[name]
                msg = 'Testing file "{}" and sheet "{}"'.format(path, name)
                self.assertEqual(expected, found, msg=msg)
