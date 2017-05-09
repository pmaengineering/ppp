"""Module for the Xlstab class."""
from collections import namedtuple
import logging

from pmix.error import XlsformError
from pmix.worksheet import Worksheet


class Xlstab(Worksheet):
    """Class to represent a tab in an XLSForm, such as "survey".

    Class attributes:
        SURVEY_TRANSLATIONS (tuple of str): The columns in "survey" that
            can be translated.
        CHOICES_TRANSLATIONS (tuple of str): The columns in "choices" or
            "external_choices" that can be translated.
        TCellData (namedtuple): A named tuple to carry specific data for
            translations.
    """

    SURVEY_TRANSLATIONS = (
        'label',
        'hint',
        'constraint_message',
        'audio',
        'video',
        'image'
    )

    CHOICES_TRANSLATIONS = (
        'label',
        'audio',
        'video',
        'image'
    )

    TCellData = namedtuple('TCellData', ['row', 'col', 'header', 'cell',
                           'language'])

    def __init__(self, *, data=None, name=None):
        """Initialize an Xlstab.

        See Worksheet for default implementation.

        Args:
            data: Data for the worksheet
            name (str): The name of the worksheet.
        """
        super().__init__(data=data, name=name)
        self.assert_unique_cols()

    def assert_unique_cols(self):
        """Throw an error if non-empty column headers are not unique."""
        headers = self.column_headers()
        found = list(filter(None, headers))
        unique = set(found)
        if len(found) != len(unique):
            raise XlsformError('Headers not unique in {}'.format(self.name))

    @classmethod
    def from_worksheet(cls, worksheet):
        """Create an instance of Xlstab from a Worksheet instance."""
        xlstab = cls(data=worksheet.data, name=worksheet.name)
        return xlstab

    def add_language(self, language):
        """Add the used translatable columns in the given language.

        Args:
            language (str or sequence): The language(s) to add
        """
        if isinstance(language, str):
            language = [language]
        translate_columns = ()
        if self.name == 'survey':
            translate_columns = self.SURVEY_TRANSLATIONS
        elif self.name in ('choices', 'external_choices'):
            translate_columns = self.CHOICES_TRANSLATIONS
        headers = self.column_headers()
        to_translate = []
        for col in translate_columns:
            if any(h.startswith(col) for h in headers):
                to_translate.append(col)
        for col in to_translate:
            for lang in language:
                header = '{}::{}'.format(col, lang)
                self.append_col(header)

    def translation_pairs(self, ignore=None):
        """Iterate through translation pairs in this tab.

        This function only works for 'survey', 'choices' and
        'external_choices'.

        The program searches for specific columns (class attributes).

        Args:
            ignore: A sequence of strings. If the header contains any of these
                then that column is ignored for translations. It is intended
                as a way to ignore certain languages. Default None indicates
                do not ignore any translatable columns.

        Yields:
            Yields pairs of translations from ``Worksheet.column_pairs``.
        """
        if ignore is None:
            ignore = []
        translate_columns = ()
        if self.name == 'survey':
            translate_columns = self.SURVEY_TRANSLATIONS
        elif self.name in ('choices', 'external_choices'):
            translate_columns = self.CHOICES_TRANSLATIONS
        for col in translate_columns:
            found = [h for h in self.column_headers() if h.startswith(col)]
            keep = [h for h in found if not any(l in h for l in ignore)]
            gen = (h for h in keep if self.get_lang(h) == 'English')
            base = next(gen, None)
            for pair in self.column_pairs(keep, base, start=1):
                base, other = pair
                base_lang = self.get_lang(base.header)
                new_base = self.TCellData(*base, base_lang)
                other_lang = self.get_lang(other.header)
                new_other = self.TCellData(*other, other_lang)
                yield new_base, new_other

    def lazy_translation_pairs(self, ignore=None, base='English'):
        """Iterate through translation pairs in this tab.

        This method is based on finding things of the form

            [column]::[language]

        in the questionnaire, matching based on [column].

        Args:
            ignore (seq of str): If the header contains any of these
                then that column is ignored for translations. It is intended
                as a way to ignore certain languages. Default None indicates
                do not ignore any translatable columns.
            base (str): The base language. The default is 'English'.

        Yields:
            Yields pairs of translations from ``Worksheet.column_pairs``.
        """
        if ignore is None:
            ignore = []
        headers = self.column_headers()
        ending = '::{}'.format(base)
        found = [h for h in headers if h.endswith(ending)]
        for col in found:
            start, _ = col.rsplit(sep='::', maxsplit=1)
            others = [h for h in headers if h.startswith(start) and h != col]
            for pair in self.column_pairs(others, col, start=1):
                first, second = pair
                base_lang = self.get_lang(first.header)
                new_base = self.TCellData(*first, base_lang)
                other_lang = self.get_lang(second.header)
                new_other = self.TCellData(*second, other_lang)
                if base_lang not in ignore and other_lang not in ignore:
                    yield new_base, new_other

    @staticmethod
    def get_lang(header):
        """Get the language from a header.

        Args:
            header (str): The header, e.g. 'label::English'

        Returns:
            The language found or None if '::' is not present
        """
        lang = None
        if '::' in header:
            lang = header.split('::', maxsplit=1)[1]
        return lang


    # generator returns two dictionaries, each of the same format
    # {
    #   constants.LANGUAGE: "English",
    #   constants.LOCATION: (row, col),
    #   constants.TEXT:     "What is your name?"
    # }
    # First dictionary is for English. Second is for the foreign language
    # def translation_pairs(self, ignore=None):
    #     if ignore is None:
    #         ignore = []
    #     try:
    #         english, others, translations = self.preprocess_header()
    #         for row, line in enumerate(self):
    #             if row == 0:
    #                 continue
    #             for eng_col, name in english:
    #                 eng_text = line[eng_col]
    #                 eng_text = eng_text.strip()
    #                 eng_dict = {
    #                     constants.LANGUAGE: constants.ENGLISH,
    #                     constants.LOCATION: (row, eng_col),
    #                     constants.TEXT:     eng_text
    #                 }
    #                 these_translations = translations[name]
    #                 for lang in others:
    #                     if lang in ignore:
    #                         continue
    #                     try:
    #                         lang_col = these_translations[lang]
    #                         lang_text = line[lang_col]
    #                         lang_text = lang_text.strip()
    #                         lang_dict = {
    #                             constants.LANGUAGE: lang,
    #                             constants.LOCATION: (row, lang_col),
    #                             constants.TEXT:     lang_text
    #                         }
    #                         # We want to consider it as needing a translation
    #                         # if there is English text defined.
    #                         # TODO this may need to change
    #                         if eng_text != '':
    #                             yield eng_dict, lang_dict
    #                     except KeyError:
    #                         # Translation not found, skip
    #                         pass
    #     except SpreadsheetError:
    #         # Nothing found from preprocess_header
    #         return

    def merge_translations(self, translations, ignore=None):
        if isinstance(translations, TranslationDict):
            for eng, lang in self.translation_pairs(ignore):
                eng_text = eng[constants.TEXT]
                if eng_text == '':
                    self.format_missing_text(eng[constants.LOCATION], eng_text)
                    continue
                lang_text = lang[constants.TEXT]
                other_lang = lang[constants.LANGUAGE]
                location = lang[constants.LOCATION]
                try:
                    translated_eng = translations.get_numbered_translation(
                        eng_text, other_lang)
                    self.update_singleton(lang_text, translated_eng, location)
                except KeyError:
                    # Might be wrong exception
                    self.format_missing_translation(location, lang_text)

    def update_singleton(self, prev_text, new_text, location):
        if prev_text != new_text:
            line = self.data[location[0]]
            line[location[1]] = new_text
            if new_text == '':
                self.format_missing_text(location, prev_text)
            elif prev_text != '':
                self.format_overwrite_text(location, new_text)

    def format_missing_text(self, location, text):
        d = {
                constants.BG_COLOR_KEY: constants.HIGHLIGHT_RED,
                constants.LOCATION: location,
                constants.TEXT: text
        }
        self.style.append(d)

    def format_overwrite_text(self, location, text):
        d = {
                constants.BG_COLOR_KEY: constants.HIGHLIGHT_BLUE,
                constants.LOCATION: location,
                constants.TEXT: text
        }
        self.style.append(d)

    def format_missing_translation(self, location, text):
        d = {
                constants.BG_COLOR_KEY: constants.HIGHLIGHT_GREEN,
                constants.LOCATION: location,
                constants.TEXT: text
        }
        self.style.append(d)

    # returns list of tuples for English columns
    # returns sorted list of languages found that are translations
    # returns dict of dictionaries to find where translations are
    def preprocess_header(self):
        if not self.data:
            m = 'No data found in worksheet "{}"'.format(self.name)
            raise SpreadsheetError(m)
        header = self.data[0]
        # list of tuples, index and column name, e.g. (4, 'hint')
        english = []
        for i, cell in enumerate(header):
            if cell.endswith(constants.ENGLISH_SUFFIX):
                # e.g. from "label::English", keep "label"
                english.append((i, cell[:-len(constants.ENGLISH_SUFFIX)]))
        if not english:
            m = 'No column labeled English found in worksheet "{}"'
            m = m.format(self.name)
            raise SpreadsheetError(m)

        # to contain all OTHER (non-English) languages used in the header
        other_languages = set()
        # Build a dict with keys that are columns ending with "::English" and
        # values are dicts them that have key -> value as language -> column
        # e.g. {label: {Hindi: 10, French: 11}, hint: {Hindi: 12, French: 13}}
        translation_lookup = {}
        for i, column in english:
            # e.g. take "hint" and make "hint::"
            prefix = constants.COL_FORMAT.format(column)
            translations = [item for item in enumerate(header) if item[0] != i
                            and item[1].startswith(prefix)]
            these_langs = {lang[len(prefix):]: j for j, lang in translations}
            translation_lookup[column] = these_langs
            other_languages |= set(these_langs.keys())
        others = list(other_languages)
        others.sort()
        return english, others, translation_lookup

    def create_translation_dict(self, ignore=None):
        result = TranslationDict()
        for eng, lang in self.translation_pairs(ignore):
            eng_text = eng[constants.TEXT]
            # only add translations if the english exists first
            if eng_text == '':
                continue
            lang_text = lang[constants.TEXT]
            other_lang = lang[constants.LANGUAGE]
            result.add_translation(eng_text, lang_text, other_lang)
        return result
