import xlrd

from error import SpreadsheetError
from verbiage import TranslationDict
import constants


class Worksheet:
    count = 0

    def __init__(self, data=None, name=None, datemode=None):
        self.data = []
        self.style = []
        for i in range(data.nrows):
            cur_row = []
            for j, cell in enumerate(data.row(i)):
                this_value = self.cell_value(cell, datemode, unicode=True)
                cur_row.append(this_value)
            self.data.append(cur_row)

        if name is None:
            Worksheet.count += 1
            self.name = constants.DEFAULT_WS_NAME + str(Worksheet.count)
        else:
            self.name = name

    # generator returns two dictionaries, each of the same format
    # {
    #   constants.LANGUAGE: "English",
    #   constants.LOCATION: (row, col),
    #   constants.TEXT:     "What is your name?"
    # }
    # First dictionary is for English. Second is for the foreign language
    def translation_pairs(self):
        try:
            english, others, translations = self.preprocess_header()
            for row, line in enumerate(self):
                if row == 0:
                    continue
                for eng_col, name in english:
                    eng_text = line[eng_col]
                    eng_text = eng_text.strip()
                    eng_dict = {
                        constants.LANGUAGE: constants.ENGLISH,
                        constants.LOCATION: (row, eng_col),
                        constants.TEXT:     eng_text
                    }
                    these_translations = translations[name]
                    for lang in others:
                        try:
                            lang_col = these_translations[lang]
                            lang_text = line[lang_col]
                            lang_text = lang_text.strip()
                            lang_dict = {
                                constants.LANGUAGE: lang,
                                constants.LOCATION: (row, lang_col),
                                constants.TEXT:     lang_text
                            }
                            if eng_text != '' and lang_text != '':
                                yield eng_dict, lang_dict
                        except KeyError:
                            # Translation not found, skip
                            pass
        except SpreadsheetError:
            # Nothing found from preprocess_header
            return

    def merge_translations(self, translations):
        if isinstance(translations, TranslationDict):
            for eng, lang in self.translation_pairs():
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

    def create_translation_dict(self):
        result = TranslationDict()
        for eng, lang in self.translation_pairs():
            eng_text = eng[constants.TEXT]
            # only add translations if the english exists first
            if eng_text == '':
                continue
            lang_text = lang[constants.TEXT]
            other_lang = lang[constants.LANGUAGE]
            result.add_translation(eng_text, lang_text, other_lang)
        return result

    def get_columns(self):
        if self.data:
            return self.data[0]
        else:
            return []

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, key):
        return self.data[key]

    def __len__(self):
        return len(self.data)

    @staticmethod
    def cell_value(cell, datemode=None, unicode=True):
        if cell.ctype == xlrd.XL_CELL_BOOLEAN:
            if unicode:
                return 'TRUE' if cell.value == 1 else 'FALSE'
            else:
                return True if cell.value == 1 else False
        elif cell.ctype == xlrd.XL_CELL_EMPTY:
            if unicode:
                return ''
            else:
                return None
        elif cell.ctype == xlrd.XL_CELL_TEXT:
            # Do I want to have the leading and trailing whitespace trimmed?
            s = cell.value.strip()
            return s
        elif cell.ctype == xlrd.XL_CELL_NUMBER:
            if int(cell.value) == cell.value:
                if unicode:
                    return str(int(cell.value))
                else:
                    return int(cell.value)
            else:
                if unicode:
                    return str(cell.value)
                else:
                    return cell.value
        elif cell.ctype == xlrd.XL_CELL_DATE:
            date_tuple = xlrd.xldate_as_tuple(cell.value, datemode)
            return '-'.join((str(x) for x in date_tuple))
        else:
            m = 'Bad cell type: {}. Value is: {}'.format(cell.ctype, cell.value)
            raise TypeError(m)
