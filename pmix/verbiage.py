"""Module for capturing translations from XLSForms."""
import logging

import xlsxwriter

import pmix.utils as utils
import pmix.workbook
import pmix.xlsform


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
    """

    def __init__(self, src=None, base='English'):
        """Initialize a translation dictionary.

        Args:
            src: A source workbook or xlsform that has translations.
            base (str): The base language for this dictionary.

        Attributes:
            data (dict): Data structure described above
            correct (set): A set of base language keys in data that are
                considered correct
            base (str): The base language
        """
        self.data = {}
        self.correct = set()
        self.base = base
        if src:
            self.extract_translations(src)

    def extract_translations(self, obj, correct=False):
        """Get translations from an object.

        This method determines the type that the object is, and then
        dispatches to other sub-methods.

        Args:
            obj: A source object, either Xlsform or Workbook
            correct (bool): Whether or not the input file is treated as correct.
        """
        if isinstance(obj, pmix.xlsform.Xlsform):
            self.translations_from_xlsform(obj, correct)
        elif isinstance(obj, pmix.workbook.Workbook):
            self.translations_from_workbook(obj, correct)

    def translations_from_xlsform(self, xlsform, correct=False):
        """Get translations from an Xlsform object.

        This uses the Xlsform's lazy_translation_pairs method.

        Args:
            xlsform (Xlsform): The Xlsform object to get translations from.
            correct (bool): Whether or not the input file is treated as correct.
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
                self.add_translation(src, second, language, correct)

    def translations_from_workbook(self, workbook, correct=False):
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
                    self.add_translation(src, second, lang, correct)
            except ValueError:
                # TODO: possibly match text::English to other columns
                pass

    def add_translation(self, src, other, lang, correct=False):
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
            correct (bool): Whether or not the input file is treated as correct.
        """
        cleaned_src = utils.td_clean_string(src)
        cleaned_other = utils.td_clean_string(str(other['cell']))
        other['translation'] = cleaned_other
        if not correct and cleaned_src in self.correct:
            # Currently not a correct translation, but we have correct
            return
        elif correct and cleaned_src not in self.correct and cleaned_src in \
                self.data:
            # Remove the old, non-correct translation
            self.data.pop(cleaned_src, None)
        if correct:
            self.correct.add(cleaned_src)
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
            sorted_all_found = sorted(unique_all_found)
            msg = msg.format(src, len(unique_all_found), sorted_all_found)
            logging.warning(msg)
        max_count = max((all_found.count(s) for s in unique_all_found))
        first_max = next((s for s in all_found if all_found.count(s) ==
                          max_count))
        return first_max

    def count_unique_translations(self, src, lang):
        """Count the translations for a given key in the given language.

        Args:
            src (str): The text that is translated
            lang (str): The language in which it is translated

        Returns:
            An integer of how many translations are found for the given source
            text
        """
        # Set the default return value to 0
        count_unique = 0
        # Clean source text
        cleaned_src = utils.td_clean_string(src)
        # If the text key is in translations
        if cleaned_src in self.data:
            # Get all translations for a given key
            all_src_data = self.data[cleaned_src]
            # If the language is among the translations
            if lang in all_src_data:
                # Collect all the unique translation strings
                translations = all_src_data[lang]
                all_found = [other['translation'] for other in translations]
                unique_all_found = set(all_found)
                # Set the return value to the size of the set
                count_unique = len(unique_all_found)
        return count_unique

    def get_unique_translations(self, src, lang):
        """Return the unique translations for a given text in a given language.

        Args:
            src (str): The text that is translated
            lang (str): The language in which it is translated

        Returns:
            A list of sorted, unique translations
        """
        # Set the default return value to an empty list
        unique = []
        # Clean source text
        cleaned_src = utils.td_clean_string(src)
        # If the text key is in translations
        if cleaned_src in self.data:
            # Get all translations for a given key
            all_src_data = self.data[cleaned_src]
            # If the language is among the translations
            if lang in all_src_data:
                # Collect all the unique translation strings
                translations = all_src_data[lang]
                all_found = [other['translation'] for other in translations]
                unique_all_found = set(all_found)
                # Set the return value to the size of the set
                unique = sorted(list(unique_all_found))
        return unique

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
        number, _ = utils.td_split_text(src)
        cleaned_src = utils.td_clean_string(src)
        clean_translation = self.get_translation(cleaned_src, lang)
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
        """Write translation data to an Excel spreadsheet.

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
        header_row = ['text::{}'.format(lang) for lang in all_languages]
        ws.write_row(0, 0, header_row)
        for i, k in enumerate(self.data):
            ws.write(i + 1, 0, k)
            for j, lang in enumerate(other_languages):
                try:
                    translation = self.get_translation(k, lang)
                    ws.write(i + 1, j + 1, translation)
                except KeyError:
                    # Missing information is highlighted
                    ws.write(i + 1, j + 1, '', red_background)

    def write_diverse_excel(self, path, language):
        """Write translation duplicate data to an Excel spreadsheet.

        Args:
            path (str): String path to write the MS-Excel file
            language (str): The language to find duplicates
        """
        wb = xlsxwriter.Workbook(path)
        red_background = wb.add_format()
        red_background.set_bg_color('#FFAAA5')
        ws = wb.add_worksheet('translations')
        all_languages = [self.base, language]
        header_row = ['text::{}'.format(lang) for lang in all_languages]
        ws.write_row(0, 0, header_row)
        dups = []
        for key in self.data:
            found = self.get_unique_translations(key, language)
            if len(found) > 1:
                dups.append((key, found))
        for i, item in enumerate(dups):
            ws.write(i + 1, 0, item[0])
            for j, translation in enumerate(item[1]):
                if j == 0:
                    ws.write(i + 1, j + 1, translation)
                else:
                    ws.write(i + 1, j + 1, translation, red_background)

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
