import re

import xlsxwriter

import constants
import utils


class TranslationDict:
    """
    Intermediate product is a dictionary
    {
        "eng-string1" : {
            "language1" : ["found1", "found2", ...]
            "language2" : ["found1", "found2", ...]
        },
        "eng-string2" : ...
    }
    """

    def __init__(self):
        self.data = {}
        self.languages = set()
        number_re = r'^([A-Z]|(\S*\d+[a-z]?))(\.|:)\s+'
        self.number_prog = re.compile(number_re)

    def add_translation(self, eng, foreign, lang):
        eng = self.clean_string(eng)
        foreign = self.clean_string(foreign)
        try:
            this_dict = self.data[eng]
            if lang in this_dict:
                this_dict[lang].append(foreign)
            else:
                this_dict[lang] = [foreign]
        except KeyError:
            self.data[eng] = {lang: [foreign]}
        self.languages.add(lang)

    def get_translation(self, eng, lang):
        this_dict = self.data[eng]
        all_found = this_dict[lang]
        max_count = max((all_found.count(s) for s in set(all_found)))
        first_max = next((s for s in all_found if all_found.count(s) ==
                          max_count))
        return first_max

    def get_numbered_translation(self, eng, lang):
        number = self.get_number(eng)
        eng = self.clean_string(eng)
        clean_translation = self.get_translation(eng, lang)
        numbered_translation = number + clean_translation
        return numbered_translation

    def update(self, other):
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

    def write_out(self, path):
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

    def get_number(self, s):
        s = s.strip()
        m = self.number_prog.match(s)
        if m:
            number = s[m.span()[0]:m.span()[1]]
        else:
            number = ''
        return number

    def clean_string(self, s):
        s = s.replace('\r', '\n')
        s = s.strip()
        s = utils.space_newline_fix(s)
        s = utils.newline_space_fix(s)
        m = self.number_prog.match(s)
        if m:
            s = s[m.span()[1]:]
            s = s.strip()
        return s

    def __str__(self):
        return str(self.data)

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, key):
        return self.data[key]
