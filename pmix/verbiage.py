# The MIT License (MIT)
#
# Copyright (c) 2016 James K. Pringle
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Module for capturing translations from XLSForms

Created: 3 October 2016
Last modified: 5 October 2016
Author: James K. Pringle
E-mail: jpringle@jhu.edu
"""

import re

import xlsxwriter

import constants
import utils


class TranslationDict:
    """Store translations with English source into any foreign language

    The translation structure is a dictionary that looks like:

        {
            "eng-string1" : {
                "language1" : ["found1", "found2", ...]
                "language2" : ["found1", "found2", ...]
            },
            "eng-string2" : ...
        }

    Keys are English strings. Values are dictionaries with language as key and
    all found translations in that language as values.

    Attributes:
        data (dict): Data structure described above
        languages (set of str): Keeps track of what languages are included
        number_prog (regex): A regex program to detect numbering schemes at the
            beginning of a string. Examples are 'HQ1. ', 'Q. ', '401a. ', and
            'LCL_010. '. Currently (10/5/2016) numbering scheme must end with
            '.', ':', or ')' and then whitespace.
    """

    def __init__(self):
        self.data = {}
        self.languages = set()
        number_re = r'^\s*([A-Z]|(\S*\d+[a-z]?))[\.:\)]\s+'
        self.number_prog = re.compile(number_re)

    def add_translation(self, eng, other, lang):
        """Add a translation to the dictionary

        Many strings to be added come from questionnaires where a numbering
        scheme is used. The question number is removed from the text if it is
        discovered using the `number_prog` attribute.

        Args:
            eng: String in English
            other: String in other language that is a translation of `eng`
            lang: String name of other language
        """
        eng = self.clean_string(eng)
        other = self.clean_string(other)
        try:
            this_dict = self.data[eng]
            if lang in this_dict:
                this_dict[lang].append(other)
            else:
                this_dict[lang] = [other]
        except KeyError:
            self.data[eng] = {lang: [other]}
        self.languages.add(lang)

    def get_translation(self, eng, lang):
        """Return a translation for an English string

        No attempt is made to remove a numbering scheme. The English string is
        translated as it is.

        Args:
            eng: String in English
            lang: String name of other language

        Returns:
            String in other language that is a translation of `eng`. If there
            are multiple translations for `eng` in `lang`, then the first most
            common translation is returned.
        """
        this_dict = self.data[eng]
        all_found = this_dict[lang]
        max_count = max((all_found.count(s) for s in set(all_found)))
        first_max = next((s for s in all_found if all_found.count(s) ==
                          max_count))
        return first_max

    def get_numbered_translation(self, eng, lang):
        """Return a translation for an English string, respecting numbering

        Since many strings come from questionnaires with a numbering scheme,
        this method first removes the number, then translates the numberless
        text, and finally adds the number back.

        Args:
            eng: String in English
            lang: String name of other language

        Returns:
            String in other language that is a translation of `eng`. This
            string also has the same numbering as `eng`.
        """
        number, _ = self.split_text(eng)
        eng = self.clean_string(eng)
        clean_translation = self.get_translation(eng, lang)
        numbered_translation = number + clean_translation
        return numbered_translation

    def update(self, other):
        """Merge another TranslationDict into this one

        Args:
            other: TranslationDict to consume

        Raises:
            TypeError: If `other` is not a TranslationDict
        """
        if isinstance(other, TranslationDict):
            self.languages |= other.languages
            for k in other:
                try:
                    this_dict = self.data[k]
                    other_dict = other[k]
                    for lang in other_dict:
                        if lang in this_dict:
                            this_dict[lang].extend(other_dict[lang])
                        else:
                            this_dict[lang] = other_dict[lang]
                except KeyError:
                    self.data[k] = other[k]
        else:
            raise TypeError(other)

    def write_out(self, path):
        """Write data to an Excel spreadsheet

        An MS-Excel spreadsheet can easily handle unicode and entries with
        newlines. It also supports coloring to highlight missing data.

        Args:
            path: String path to write the MS-Excel file
        """
        languages = list(self.languages)
        wb = xlsxwriter.Workbook(path)
        red_background = wb.add_format()
        red_background.set_bg_color(constants.HIGHLIGHT_XL_RED)
        ws = wb.add_worksheet(constants.TRANSLATION_WS_NAME)
        all_languages = [constants.ENGLISH] + languages
        heading = [constants.BOTH_COL_FORMAT.format(constants.TEXT, h) for h
                   in all_languages]
        ws.write_row(0, 0, heading)
        for i, k in enumerate(self.data):
            ws.write(i + 1, 0, k)
            for j, lang in enumerate(languages):
                try:
                    translation = self.get_translation(k, lang)
                    ws.write(i + 1, j + 1, translation)
                except KeyError:
                    # Missing information is highlighted
                    ws.write(i + 1, j + 1, '', red_background)

    def split_text(self, s):
        """Split text into a number and the rest

        This splitting is done using the regex attribute `number_prog`.

        Args:
            s: String to split

        Returns:
            A tuple `(number, text)`. The original string is `number + text`.
            If no number is found with the regex, then `number` is '', the
            empty string.
        """
        m = self.number_prog.match(s)
        if m:
            number = s[m.span()[0]:m.span()[1]]
            text = s[m.span()[1]:]
        else:
            number = ''
            text = s
        return number, text

    def clean_string(self, s):
        """Clean a string for addition into the translation dictionary

        Leading and trailing whitespace is removed. Newlines are converted to
        the UNIX style. Opening number is removed if found by `split_text`.

        Args:
            s: String to be cleaned.

        Returns:
            A cleaned string with number removed.
        """
        s = s.strip()
        s = s.replace('\r\n', '\n')
        s = s.replace('\r', '\n')
        s = utils.space_newline_fix(s)
        s = utils.newline_space_fix(s)
        _, text = self.split_text(s)
        return text

    def __str__(self):
        return str(self.data)

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, key):
        return self.data[key]
