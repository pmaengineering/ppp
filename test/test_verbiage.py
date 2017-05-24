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

from pmix.verbiage import TranslationDict


class TranslationDictTest(unittest.TestCase):
    """Unit tests for the TranslationDict class"""

    def test_yes_split_text(self):
        yes_split = (
            ('SIQ4. Where did you hear about bilharzia?', 'SIQ4. '),
            ('M-2.  Are you menstruating today? ', 'M-2.  '),
            ('G. In what month and year were you born?', 'G. '),
            ('B. Your name:', 'B. '),
            ('SIQ29. What is your tribe?', 'SIQ29. '),
            ('CCA-4. What is the test result?', 'CCA-4. '),
            ('CCA-5a. The test is positive.', 'CCA-5a. '),
            ('P.  Questionnaire result', 'P.  '),
            ('M. Résultat du Questionnaire', 'M. '),
            ('QF24a. Vous avez dit que vous n’utilisez pas...', 'QF24a. '),
            ('QF1. Quel âge aviez-vous à votre dernier...?', 'QF1. '),
            ('114c.1. My nutrition question', '114c.1. '),
            ('114c.d.i. My falsified question', '114c.d.i. '),
            ('411i. Post pregnancy usage', '411i. ')
        )
        td = TranslationDict()
        for s, n in yes_split:
            number, text = td.split_text(s)
            msg = 'Found "{}", expected "{}"'.format(number, n)
            self.assertTrue(number == n, msg=msg)

    def test_no_split_text(self):
        self.longMessage = True
        no_split = (
            'READ THIS WARNING: This individual questionnaire...',
            'Press OK to continue',
            'Region:',
            'Enumeration Area:',
            'Previously, ${cg_SHQ} was indicated as a caregiver...',
            'Ask ${cg_SIQ}: SIQ13. ${firstname} atera  okufuka  mu  nsiko?',
            'CHECK: Is anyone other than ${firstname} present at this time?',
            '${firstname}: is married.',
            'Section 3 - Bilharzia History',
            'ERROR: Start of filtration is before the collection time. ',
            '',
        )
        td = TranslationDict()
        for s in no_split:
            number, text = td.split_text(s)
            msg = 'Number present in "{}"'.format(s)
            self.assertTrue(number == '', msg=msg)

if __name__ == '__main__':
    unittest.main()
