"""
Supply source XLSForm

get the translations from different file(s)
"""

import argparse
import os.path

from translation import TranslationDict
import constants
import spreadsheet



#### CODE BELOW SLATED FOR DELETION
# def translation_dict_from_file(f):
#     result = TranslationDict()
#     wb = spreadsheet.Workbook(f)
#     source_worksheets = [
#         constants.SURVEY,
#         constants.CHOICES,
#         constants.TRANSLATION_WS_NAME
#     ]
#     for sheetname in source_worksheets:
#         try:
#             ws = wb[sheetname]
#             this_dict = create_translation_dict(ws)
#             result.update(this_dict)
#         except KeyError:
#             # Sheetname not found in workbook. That is OK.
#             pass
#     return result
#
#
# # give me a worksheet, and I will give you
# def create_translation_dict(ws):
#     result = TranslationDict()
#     header = ws[0]
#     try:
#         english, others, translations = qlang.preprocess_header(header)
#         for line in ws[1:]:
#             found = extract_line_translations(line, english, others, translations)
#             result.update(found)
#     except QlangError:
#         # English not found, do nothing
#         pass
#     return result
#
#
# def extract_line_translations(line, english, others, translations):
#     result = TranslationDict()
#     for col, name in english:
#         eng = line[col]
#         if eng == '':
#             continue
#         these_translations = translations[name]
#         for lang in others:
#             try:
#                 this_col = these_translations[lang]
#                 foreign = line[this_col]
#                 result.add_translation(eng, foreign, lang)
#             except KeyError:
#                 # This language not found... unlikely
#                 pass
#     return result
#### CODE ABOVE SLATED FOR DELETION


def translation_dict_from_files(files):
    result = TranslationDict()
    workbooks = [spreadsheet.Workbook(f) for f in files]
    for wb in workbooks:
        this_dict = wb.create_translation_dict()
        result.update(this_dict)
    return result


def get_wb_outpath(wb):
    orig = wb.file
    base, ext = os.path.splitext(orig)
    outpath = '{}{}{}'.format(base, constants.BORROW_SUFFIX, ext)
    return outpath


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


    translation_dict = translation_dict_from_files(set(args.xlsxfile))
    if args.merge is None:
        outpath = constants.BORROW_OUT if args.outpath is None else args.outpath
        translation_dict.write_out(outpath)
        print('Created translation file: "{}"'.format(outpath))
    else:
        wb = spreadsheet.Workbook(args.merge)
        wb.merge_translations(translation_dict)
        outpath = get_wb_outpath(wb) if args.outpath is None else args.outpath
        wb.write_out(outpath)
        print('Merged translations into file: "{}"'.format(outpath))
