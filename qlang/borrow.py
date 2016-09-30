"""
Supply source XLSForm

get the translations from different file(s)
"""

import xlsxwriter

import argparse
import re

import qlang 
from qlang import QlangError
import spreadsheet


class TranslationDict():
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

    def update(self, other):
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

    def write_out(self, path):
        languages = list(self.languages)
        wb = xlsxwriter.Workbook(path)
        ws = wb.add_worksheet('translations')
        ws.write_row(0, 0, ['English'].extend(languages))
        for i, k in enumerate(self.data):
            ws.write(i+1, 0, k)
            translations = self.data[k]
            for j, lang in enumerate(languages):
                try:
                    pass
                except:
                    pass


    @staticmethod
    def clean_string(s):
        s = s.replace('\r', '\n')
        s = s.strip()
        s = qlang.space_newline_fix(s)
        number_re = r'^([A-Z]|(\S*\d+[a-z]?))(\.|:)\s+'
        m = re.match(number_re, s)
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

def extract_line_translations(line, english, others, translations):
    result = TranslationDict()
    for col, name in english:
        eng = line[col]
        if eng == '':
            continue
        these_translations = translations[name]
        for lang in others:
            try:
                this_col = these_translations[lang]
                foreign = line[this_col]
                result.add_translation(eng, foreign, lang)
            except KeyError:
                # This language not found... unlikely
                pass
    return result


# give me a worksheet, and I will give you
def create_translation_dict(ws):
    result = TranslationDict()
    header = ws[0]
    try:
        english, others, translations = qlang.preprocess_header(header) 
        for line in ws[1:]:
            found = extract_line_translations(line, english, others, translations)
            result.update(found)
    except QlangError:
        # English not found, do nothing
        pass
    print(result)
    return result


if __name__ == '__main__':
    prog_desc = 'Grab translations from existing XLSForms'
    parser = argparse.ArgumentParser(description=prog_desc)

    file_help = 'One or more paths to source XLSForms containing translations.'
    parser.add_argument('xlsxfile', nargs='+', help=file_help)

    merge_help = 'An XLSForm that receives the translations from source files.'
    parser.add_argument('-m', '--merge', help=merge_help)

    out_help = 'Path to write output.'
    parser.add_argument('-o', '--outpath', help=out_help)

    args = parser.parse_args()

    print("Received")
    print("Files: ", args.xlsxfile)
    print("Merge: ", args.merge)
    print("Outpath: ", args.outpath)

    f = [
        'test/files/GHR5-SDP-Questionnaire-v13-jkp.xlsx',
        '/Users/jpringle/Downloads/KER5-SDP-Questionnaire-v2-jef.xlsx'
    ]
    wb = spreadsheet.Workbook(f[1])
    create_translation_dict(wb['survey'])

    # If just input files: create a dictionary of sorts that can be used later
    # If input files and out: write that dictionary to out
    # If input files and merge: add translations to merge, overwrite where needed, add entire dictionary in new worksheet
    # If input files and merge and out: above plus specified outfile

