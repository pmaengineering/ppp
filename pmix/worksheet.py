"""This module defines the Worksheet class"""

import csv

import xlrd

from pmix import constants
from pmix.cell import Cell
from pmix.error import SpreadsheetError
from pmix.verbiage import TranslationDict


class Worksheet:
    """This module represents a worksheet in a spreadsheet"""
    
    count = 0

    hl_colors = {
        'HL_YELLOW_1'   : '#FDFD96'
        'HL_YELLOW'     : '#FFFA81'
        'HL_ORANGE'     : '#FFD3B6'
        'HL_RED'        : '#FFAAA5'
        'HL_GREEN'      : '#85CA5D'
        'HL_BLUE'       : '#9ACEDF'
    }

    @classmethod
    def from_sheet(cls, sheet, datemode=None):
        """Create Worksheet from xlrd Sheet object"""
        worksheet = cls(name=sheet.name)
        for i in range(sheet.nrows):
            cur_row = [Cell.from_cell(c, datemode) for c in sheet.row(i)]
            worksheet.data.append(cur_row)
        return worksheet

    def __init__(self, *, data=None, name=None):
        if data is None:
            self.data = []
        else:
            self.data = data
        if name is None:
            Worksheet.count += 1
            self.name = constants.DEFAULT_WS_NAME + str(Worksheet.count)
        else:
            self.name = name

    def add_col(self, header=None):
        """Append a column to the end of the worksheet

        Args:
            header: The optional header for the column
        """
        for i, row in enumerate(self):
            if i == 0:
                row.append(Cell(header))
            else:
                row.append(Cell())

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

    def column_names(self):
        if self.data:
            return self.data[0]
        else:
            return []

    def column(self, i):
        if isinstance(i, str):
            try:
                col = self.column_names().index(i)
            except ValueError:
                raise KeyError(i)
        elif isinstance(i, int):
            col = i
        else:
            raise KeyError(i)
        for row in self:
            yield row[col]

    def to_csv(self, filename):
        with open(filename, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            for row in self:
                csv_writer.writerow(row)

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, key):
        return self.data[key]

    def __len__(self):
        return len(self.data)

