"""Module for the Xlstab class."""
from pmix.error import XlsformError
from pmix.worksheet import Worksheet


class Xlstab(Worksheet):
    """Class to represent a tab in an XLSForm, such as "survey".

    In contrast to the Worksheet, the Xlstab is assumed to be a regular
    dataset with unique column headers (some may be missing). If the tab name
    is important in XLSForm syntax, such as "survey", special assumptions are
    made.

    Class attributes:
        SURVEY_TRANSLATIONS (tuple of str): The columns in "survey" that
            can be translated.
        CHOICES_TRANSLATIONS (tuple of str): The columns in "choices" or
            "external_choices" that can be translated.
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

    def __init__(self, *, data=None, name=None):
        """Initialize an Xlstab.

        See Worksheet for default implementation.

        Args:
            data: Data for the worksheet
            name (str): The name of the worksheet.
        """
        super().__init__(data=data, name=name)
        self.assert_unique_cols()

    def __repr__(self):
        """Return formal representation of the Xlstab."""
        msg = '<Xlstab(name="{}"), dim={}>'.format(self.name, self.dim())
        return msg

    def assert_unique_cols(self):
        """Throw an error if non-empty column headers are not unique."""
        headers = self.column_headers()
        found = list(filter(None, headers))
        unique = set(found)
        if len(found) != len(unique):
            raise XlsformError('Headers not unique in {}'.format(self.name))

    def dict_rows(self):
        """Iterate over rows, returning dictionairy for each row.

        The column header strings are the keys for a given dictionary. The
        Cell is the value.

        Yields:
            A dictionary for each row, starting with the second row (the first
            is the header).
        """
        headers = self.column_headers()
        for i, row in enumerate(self):
            if i == 0:
                continue
            json_row = {k: v for k, v in zip(headers, row)}
            yield json_row

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

    def translation_pairs(self, ignore=None, base='English'):
        """DEPRECATED: Iterate through translation pairs in this tab.

        This function only works for 'survey', 'choices' and
        'external_choices'.

        The program searches for specific columns (class attributes).

        Args:
            ignore: A sequence of strings. If the header contains any of these
                then that column is ignored for translations. It is intended
                as a way to ignore certain languages. Default None indicates
                do not ignore any translatable columns.

        Yields:
            A dictionary.
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
            gen = (h for h in keep if self.get_lang(h) == base)
            base_col = next(gen, None)
            for pair in self.column_pairs(keep, base_col, start=1):
                src, other = pair
                src_lang = self.get_lang(src['header'])
                src['language'] = src_lang
                other_lang = self.get_lang(other['header'])
                other['language'] = other_lang
                if src_lang in ignore or other_lang in ignore:
                    continue
                if src['cell'].is_blank() or other['cell'].is_blank():
                    continue
                yield src, other

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
            A dictionary from `Worksheet.column_pairs` plus a new key of
            'language', the language returned from `self.get_lang`.
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
                src, other = pair
                src_lang = self.get_lang(src['header'])
                src['language'] = src_lang
                other_lang = self.get_lang(other['header'])
                other['language'] = other_lang
                if src_lang in ignore or other_lang in ignore:
                    continue
                if src['cell'].is_blank() and other['cell'].is_blank():
                    continue
                yield src, other

    def easy_translation_pairs(self, ignore=None, base='English'):
        """Iterate through translation pairs in this tab.

        This method is based on finding a column titled "English", and then
        generating pairs with all other columns after it.

        Args:
            ignore (seq of str): If the header contains any of these
                then that column is ignored for translations. It is intended
                as a way to ignore certain languages. Default None indicates
                do not ignore any translatable columns.
            base (str): The base language. The default is 'English'.

        Yields:
            A dictionary from `Worksheet.column_pairs` plus new key of
            'language' (equal to the header in this method).
        """
        if ignore is None:
            ignore = []
        try:
            base = self.column_headers().index(base)
            ncol = self.ncol()
            indices = range(base, ncol)
            for pair in self.column_pairs(indices=indices, start=1):
                src, other = pair
                if src['header'] in ignore or other['header'] in ignore:
                    continue
                if src['cell'].is_blank() and other['cell'].is_blank():
                    continue
                src['language'] = src['header']
                other['language'] = other['header']
                yield src, other
        except ValueError:
            # Base language not found. No translations
            pass

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

    def sheet_languages(self):
        """Get the sorted languages from headers.

        Examines each header in the sheet and compares against a list of
        pre-known translatable headers. If a header is translatable, then the
        language is determined. All languages found are put in a list and
        sorted.

        Returns:
            A list of languages found, sorted alphabetically. None is first if
            it is found.
        """
        translate_columns = ()
        if self.name == 'survey':
            translate_columns = self.SURVEY_TRANSLATIONS
        elif self.name in ('choices', 'external_choices'):
            translate_columns = self.CHOICES_TRANSLATIONS
        headers = self.column_headers()
        languages = set()
        for header in headers:
            for translatable in translate_columns:
                if header.startswith(translatable):
                    language = self.get_lang(header)
                    languages.add(language)
        has_none = False
        if None in languages:
            has_none = True
            languages.remove(None)
        sorted_languages = sorted(list(languages))
        if has_none:
            sorted_languages.insert(0, None)
        return sorted_languages

    def merge_translations(self, translations, ignore=None, base='English',
                           carry=False, no_diverse=False):
        """Merge translations from a TranslationDict.

        By the end of this method call, this worksheet will have translations
        filled in and colored appropriately. The highlighting rules are as
        follows:

        - Yellow if no_diverse is True and the source text has diverse
            translations.
        - Orange if the source and the translation are the same.
        - Blue if the new translation changes the old translation.
        - Green if the translation is not found in the TranslationDict, but
            there is a pre-existing translation.
        - Red if translation is not found and there is no pre-existing
            translation.
        - Grey if the translation fills in a previously missing translation.
        - No highlight if the translation is the same as the pre-existing
            translation.

        Args:
            translations (TranslationDict): The translation dictionary
            ignore (list of str): The list of languages to ignore while
                translating.
            base (str): The base language. Should probably be left as English.
            carry (bool): True if missing translations be filled in from the
                base language.
            no_diverse (bool): If true, then do not translate text that has
                multiple translations.
        """
        for src, other in self.lazy_translation_pairs(ignore, base):
            src_text = str(src['cell'])
            if src_text == '':
                continue
            other_text = str(other['cell'])
            other_lang = other['language']
            if no_diverse:
                count_unique = translations.count_unique_translations(
                        src_text, other_lang)
                if count_unique > 1:
                    other['cell'].highlight = 'HL_YELLOW'
                    continue
            try:
                translated = translations.get_numbered_translation(src_text,
                                                                   other_lang)
                other['cell'].value = translated
                if src_text == translated:
                    other['cell'].highlight = 'HL_ORANGE'
                elif translated != other_text and other_text == '':
                    other['cell'].highlight = 'HL_GREY'
                elif translated != other_text: # and other_text != ''
                    other['cell'].highlight = 'HL_BLUE'
            except KeyError:
                if other['cell'].is_blank():
                    if carry:
                        other['cell'].value = src_text
                        other['cell'].highlight = 'HL_ORANGE'
                    else:
                        other['cell'].highlight = 'HL_RED'
                else:
                    other['cell'].highlight = 'HL_GREEN'
