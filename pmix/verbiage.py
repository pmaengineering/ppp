"""Module for capturing translations from XLSForms."""
import logging
import re

import xlsxwriter

from pmix.workbook import Workbook
from pmix.xlsform import Xlsform


class TranslationDict:
    """Store translations with a base source into any foreign language.

    The translation structure is a dictionary that looks like:

        {
            "eng1" : {
                "language1" : ["found1", "found2", ...]
                "language2" : ["found1", "found2", ...]
            },
            "eng2" : ...
        }

    Keys are strings. Values are dictionaries with language string as
    key and all found translations in that language as values. The found
    translations are objects that store extra information.

    This class is essentially a wrapper around a dictionary with insert and
    lookup functions depending on a key and a language.

    Class attributes:
        number_prog (regex): A regex program to detect numbering schemes at the
            beginning of a string. Examples are 'HQ1. ', 'Q. ', '401a. ', and
            'LCL_010. '. Currently (10/5/2016) numbering scheme must end with
            '.', ':', or ')' and then possibly whitespace.
    """

    number_re = r'^\s*([A-Z]|(\S*\d+[.a-z]*))[.:)]\s+'
    number_re = r"""
                ^\s*                # Begin with possible whitespace.
                (
                    [A-Z]           # Start with a capital letter
                |
                    (
                        \S*         # or start with non-whitespace and
                        \d+         # one or more numbers, then possibly
                        [.a-z]*     # dots (.) and lower-case letters
                    )
                )
                [.:)]               # Always end with '.' ':' ')' and
                \s+                 # whitespace
                """
    # pylint: disable=no-member
    number_prog = re.compile(number_re, re.VERBOSE)

    def __init__(self, src=None, base='English'):
        """Initialize a translation dictionary.

        Args:
            src: A source workbook or xlsform that has translations.
            base (str): The base language for this dictionary.

        Attributes:
            data (dict): Data structure described above
            languages (set of str): Keeps track of what languages are included
        """
        self.data = {}
        self.base = base
        if src:
            self.extract_translations(src)

    def extract_translations(self, obj):
        """Get translations from an object.

        This method determines the type that the object is, and then
        dispatches to other sub-methods.

        Args:
            obj: A source object, either Xlsform or Workbook
        """
        if isinstance(obj, Xlsform):
            self.translations_from_xlsform(obj)
        elif isinstance(obj, Workbook):
            self.translations_from_workbook(obj)

    def translations_from_xlsform(self, xlsform):
        """Get translations from an Xlsform object.

        This uses the Xlsform's lazy_translation_pairs method.

        Args:
            xlsform (Xlsform): The Xlsform object to get translations from.
        """
        for xlstab in xlsform:
            for pair in xlstab.lazy_translation_pairs(base=self.base):
                first, second = pair
                first_cell = first['cell']
                second_cell = second['cell']
                if first_cell.is_blank() or second_cell.is_blank():
                    continue
                src = str(first_cell)
                language = second['language']
                second['file'] = xlsform.file
                second['sheet'] = xlstab.name
                self.add_translation(src, second, language)

    def translations_from_workbook(self, workbook):
        """Get translations from a workbook object.

        Probably should not be used; it is considered deprecated.

        It looks for the base language as a column header then considers
        what follows to be translations.

        Args:
            workbook (Workbook): The Workbook object to get translations from.
        """
        for worksheet in workbook:
            try:
                base = worksheet.column_headers().index(self.base)
                ncol = worksheet.ncol()
                indices = range(base, ncol)
                for pair in worksheet.column_pairs(indices=indices, start=1):
                    first, second = pair
                    first_cell = first['cell']
                    second_cell = second['cell']
                    if first_cell.is_blank() or second_cell.is_blank():
                        continue
                    src = str(first_cell)
                    lang = second_cell.header
                    second['file'] = workbook.file
                    second['sheet'] = worksheet.name
                    self.add_translation(src, second, lang)
            except ValueError:
                # TODO: possibly match text::English to other columns
                pass

    def add_translation(self, src, other, lang):
        """Add a translation to the dictionary.

        Many strings to be added come from questionnaires where a numbering
        scheme is used. The question number is removed from the text if it is
        discovered using the `number_prog` attribute.

        The cleaned translation is stored in the `other` dictionary.

        Args:
            src (str): String in the base language
            other (dict): A dictionary containing the CellData namedtuple and
                other metadata.
            lang (str): String name of other language
        """
        cleaned_src = self.clean_string(src)
        cleaned_other = self.clean_string(str(other['cell']))
        other['translation'] = cleaned_other
        try:
            this_dict = self.data[cleaned_src]
            if lang in this_dict:
                this_dict[lang].append(other)
            else:
                this_dict[lang] = [other]
        except KeyError:
            self.data[cleaned_src] = {lang: [other]}

    def get_translation(self, src, lang):
        """Return a translation for a source string.

        The source string should be in the base language for the translation
        dictionary. No attempt is made to remove a numbering scheme. The
        source string is translated as it is.

        Args:
            src (str): String in base language for this translator.
            lang (str): String name of language for the translation.

        Returns:
            String in other language that is a translation of `src`. If there
            are multiple translations for `src` in `lang`, then the first most
            common translation is returned.
        """
        this_dict = self.data[src]
        all_found_data = this_dict[lang]
        all_found = [other['translation'] for other in all_found_data]
        unique_all_found = set(all_found)
        if len(unique_all_found) > 1:
            msg = '"{}" has {} translations {}'
            msg = msg.format(src, len(unique_all_found), unique_all_found)
            logging.warning(msg)
        max_count = max((all_found.count(s) for s in unique_all_found))
        first_max = next((s for s in all_found if all_found.count(s) ==
                          max_count))
        return first_max

    def get_numbered_translation(self, src, lang):
        """Return a translation for a source string, respecting numbering.

        Since many strings come from questionnaires with a numbering scheme,
        this method first removes the number, then translates the numberless
        text, and finally adds the number back.

        Args:
            src (str): String in base language for this translator.
            lang (str): String name of language for the translation.

        Returns:
            String in other language that is a translation of `src`. This
            string also has the same numbering as `src`.
        """
        number, _ = self.split_text(src)
        src = self.clean_string(src)
        clean_translation = self.get_translation(src, lang)
        numbered_translation = number + clean_translation
        return numbered_translation

    def update(self, other):
        """Merge another TranslationDict into this one.

        Args:
            other: TranslationDict to consume

        Raises:
            TypeError: If `other` is not a TranslationDict
        """
        if isinstance(other, TranslationDict):
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

    def get_languages(self):
        """Get all non-base languages used in this translation dict.

        Returns:
            A set with the strings for all languages
        """
        all_languages = set()
        for value in self.data.values():
            for language in value:
                all_languages.add(language)
        return all_languages

    def write_excel(self, path, others=None):
        """Write data to an Excel spreadsheet.

        An MS-Excel spreadsheet can easily handle unicode and entries with
        newlines. It also supports coloring to highlight missing data.

        Args:
            path (str): String path to write the MS-Excel file
            others (list): Other languages to add to the output.
        """
        wb = xlsxwriter.Workbook(path)
        red_background = wb.add_format()
        red_background.set_bg_color('#FFAAA5')
        ws = wb.add_worksheet('translations')
        other_languages = sorted(list(self.get_languages()))
        all_languages = [self.base] + other_languages
        if others:
            for other in others:
                if other not in all_languages:
                    all_languages.append(other)
        ws.write_row(0, 0, all_languages)
        for i, k in enumerate(self.data):
            ws.write(i + 1, 0, k)
            for j, lang in enumerate(other_languages):
                try:
                    translation = self.get_translation(k, lang)
                    ws.write(i + 1, j + 1, translation)
                except KeyError:
                    # Missing information is highlighted
                    ws.write(i + 1, j + 1, '', red_background)

    @staticmethod
    def split_text(text):
        """Split text into a number and the rest.

        This splitting is done using the regex attribute `number_prog`.

        Args:
            text (str): String to split

        Returns:
            A tuple `(number, the_rest)`. The original string is `number +
            the_rest`. If no number is found with the regex, then `number` is
            '', the empty string.
        """
        number = ''
        the_rest = text
        if len(text.split()) > 1:
            match = TranslationDict.number_prog.match(text)
            if match:
                number = text[match.span()[0]:match.span()[1]]
                the_rest = text[match.span()[1]:]
        return number, the_rest

    @staticmethod
    def clean_string(text):
        """Clean a string for addition into the translation dictionary.

        Leading and trailing whitespace is removed. Newlines are converted to
        the UNIX style. Opening number is removed if found by `split_text`.

        Args:
            text (str): String to be cleaned.

        Returns:
            A cleaned string with number removed.
        """
        text = text.strip()
        text = text.replace('\r\n', '\n')
        text = text.replace('\r', '\n')
        text = TranslationDict.space_newline_fix(text)
        text = TranslationDict.newline_space_fix(text)
        _, text = TranslationDict.split_text(text)
        return text

    @staticmethod
    def newline_space_fix(text):
        """Replace "newline-space" with "newline".

        This function was particularly useful when converting between Google
        Sheets and .xlsx format.

        Args:
            text (str): The string to work with

        Returns:
            The text with the appropriate fix.
        """
        newline_space = '\n '
        fix = '\n'
        while newline_space in text:
            text = text.replace(newline_space, fix)
        return text

    @staticmethod
    def space_newline_fix(text):
        """Replace "space-newline" with "newline".

        Args:
            text (str): The string to work with

        Returns:
            The text with the appropriate fix.
        """
        space_newline = ' \n'
        fix = '\n'
        while space_newline in text:
            text = text.replace(space_newline, fix)
        return text

    def __str__(self):
        """Return a string representation of the data."""
        return str(self.data)

    def __iter__(self):
        """Return an iterator over the translated strings."""
        return iter(self.data)

    def __len__(self):
        """Get the number of base strings translated."""
        return len(self.data)

    def __getitem__(self, key):
        """Get the data associated with the key in the underlying data."""
        return self.data[key]
