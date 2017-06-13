#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for Viffer package."""
import unittest
from os import path as os_path
from pmix.viffer.__main__ import cli


TEST_FORMS_DIRECTORY = os_path.dirname(os_path.realpath(__file__))


# pylint: disable=too-few-public-methods
# PyLint check not apply? - http://pylint-messages.wikidot.com/messages:r0903
class VifferTest:
    """Base class for Viffer package tests."""

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


class OdkPromptTest(unittest.TestCase, VifferTest):
    """Unit tests for the OdkPrompt class."""

    media_types = ['image', 'audio', 'video', 'media::image',
                   'media::audio', 'media::video']
    media_lead_char = '['
    media_end_char = ']'
    arbitrary_language_param = 'English'

    def setUp(self):
        self.data = (
            ({'inputs': {
                 'files': []
            }, 'expected_outputs': {

            }},
             {'inputs': {
                 'file': []
             }, 'expected_outputs': {

             }},
            )
        )

    def test_initialization_has_choices(self):
        error = True
        if error:
            msg = 'Error.'
            self.assertTrue(error is False, msg=msg)
