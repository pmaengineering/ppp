#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os.path

import xlrd
import xlsxwriter

from error import QlangError


QLANG_PREFIX = 'qlang-'
QLANG_SUFFIX = '-qlang'
QLANG_WORKSHEET_NAME = 'translations'
QLANG_WORKSHEET = 'worksheet'
QLANG_ROW = 'row'
QLANG_TYPE = 'type'
QLANG_LIST_NAME = 'list_name'
QLANG_NAME = 'name'
QLANG_COLUMN = 'column'
ENGLISH = 'English'
TRANSLATIONS = 'translations'
ENGLISH_SUFFIX = '::{}'.format(ENGLISH)
COL_FORMAT = '{}::'
BOTH_COL_FORMAT = '{}::{}'
LANGUAGE_SEP = '::'
SURVEY = 'survey'
CHOICES = 'choices'
SETTINGS = 'settings'
SELECT_ONE = 'select_one'
SELECT_MULTIPLE = 'select_multiple'


def questionnaire_to_translations(filename, prefix):
    with xlrd.open_workbook(filename) as book:
        # if no survey worksheet, then abort (don't catch exception here
        survey_ws = book.sheet_by_name(SURVEY)
        survey, s_others = process_worksheet(survey_ws)

        c_others = []
        choices_dict = {}
        try:
            choices_ws = book.sheet_by_name(CHOICES)
            choices, c_others = process_worksheet(choices_ws)
            choices_dict = group_choices(choices)
            if set(c_others) != set(s_others):
                # TODO Allow choices and survey to start with diff other langs
                m = 'Languages not the same in the {} and {} worksheets.'
                m = m.format(SURVEY, CHOICES)
                raise QlangError(m)
        except xlrd.XLRDError as e:
            # TODO Eventually reformat what is printed. May not be an error
            print(e)
            m = 'Likely error: No "choices" worksheet found in "{}"'
            m = m.format(filename)
            print(m)
        write_out_translations(filename, prefix, s_others, survey, choices_dict)


def write_out_translations(filename, prefix, others, survey, choices_dict):
    first_part, second_part = os.path.split(filename)
    out_file = os.path.join(first_part, prefix + second_part)
    wb = xlsxwriter.Workbook(out_file)
    ws = wb.add_worksheet(QLANG_WORKSHEET_NAME)
    basic_header = [QLANG_WORKSHEET, QLANG_ROW, QLANG_TYPE, QLANG_NAME,
                    QLANG_COLUMN, ENGLISH]
    ws.write_row(0, 0, basic_header)
    ws.write_row(0, len(basic_header), others)
    n = 1
    remaining_list_names = list(choices_dict.keys())
    for line in survey:
        out_row = [line[QLANG_WORKSHEET], line[QLANG_ROW] + 1,
                     line[QLANG_TYPE], line[QLANG_NAME], line[QLANG_COLUMN],
                     line[ENGLISH]]
        out_row += line[TRANSLATIONS]
        ws.write_row(n, 0, out_row)
        n += 1
        this_type = line[QLANG_TYPE].split(None)
        has_choice_list = this_type[0] in (SELECT_ONE, SELECT_MULTIPLE)
        if has_choice_list and this_type[1] in remaining_list_names:
            these_choices = choices_dict[this_type[1]]
            for c in these_choices:
                choice_row = [c[QLANG_WORKSHEET], c[QLANG_ROW] + 1,
                              c[QLANG_TYPE], c[QLANG_NAME],
                              c[QLANG_COLUMN], c[ENGLISH]]
                choice_row += c[TRANSLATIONS]
                ws.write_row(n, 0, choice_row)
                n += 1
            remaining_list_names.remove(this_type[1])
    # TODO add conditional formatting
    red_background = wb.add_format({'bg_color':   '#FFC7CE'})
    start_col = len(basic_header)-1
    last_col = len(basic_header) + len(others) - 1
    ws.conditional_format(1, start_col, n-1, last_col, {
        'type': 'blanks',
        'format': red_background
    })
    wb.close()
    if remaining_list_names:
        print('### Unused list names in "{}"'.format(filename))
        for list_name in remaining_list_names:
            print(' - {}'.format(list_name))
    m = 'Translation file created: "{}"'.format(out_file)
    print(m)


def group_choices(choices):
    choices_dict = {}
    for line in choices:
        this_choice_list = line[QLANG_TYPE]
        if this_choice_list in choices_dict:
            choices_dict[this_choice_list].append(line)
        else:
            choices_dict[this_choice_list] = [line]
    return choices_dict


# returns list of tuples for English columns
# returns sorted list of languages found that are translations
# returns dict of dictionaries to find where translations are
def preprocess_header(header):
    # list of tuples, index and column name, e.g. (4, 'hint')
    english = []
    for i, cell in enumerate(header):
        if cell.endswith(ENGLISH_SUFFIX):
            english.append((i, cell[:-len(ENGLISH_SUFFIX)]))
    if not english:
        m = 'English not found in a worksheet'
        raise QlangError(m)

    # to contain all OTHER (non-English) languages used in the header
    other_languages = set()
    # #by end of for-loop, keys are columns with ::English. values are dicts
    # #that have language and column
    # e.g. {label: {Hindi: 10, French: 11}, hint: {Hindi: 12, French: 13}}
    # except with quotes around the strings.
    translation_lookup = {}
    for i, column in english:
        prefix = COL_FORMAT.format(column)
        translations = [item for item in enumerate(header) if item[0] != i and
                        item[1].startswith(prefix)]
        these_languages = {lang[len(prefix):]: j for j, lang in translations}
        translation_lookup[column] = these_languages
        other_languages |= set(these_languages.keys())
    others = list(other_languages)
    others.sort()
    return english, others, translation_lookup


# Return the worksheet and the list of other languages (not english)
def process_worksheet(worksheet):
    unicode = get_unicode_ws(worksheet)
    # Assumption that first row is the header
    header = unicode[0]
    english, others, translations = preprocess_header(header)
    type_col = get_type_col(header)
    name_col = header.index(QLANG_NAME)
    rows_for_output = []
    for i, row in enumerate(unicode):
        if i == 0:
            continue
        for j, column in english:
            this_cell = row[j]
            # No more blank values! Use '#####'
            if this_cell != '':
                this_dict = {}
                this_dict[QLANG_WORKSHEET] = worksheet.name
                this_dict[QLANG_ROW] = i
                this_dict[QLANG_TYPE] = row[type_col]
                this_dict[QLANG_NAME] = row[name_col]
                this_dict[QLANG_COLUMN] = column
                this_dict[ENGLISH] = this_cell
                this_dict[TRANSLATIONS] = get_translations(row, others,
                                                           translations[column])
                rows_for_output.append(this_dict)
    return rows_for_output, others


def get_type_col(header):
    if QLANG_TYPE in header:
        col = header.index(QLANG_TYPE)
    elif QLANG_LIST_NAME in header:
        col = header.index(QLANG_LIST_NAME)
    else:
        m = 'Unable to find "{}" or "{}" in header'
        m = m.format(QLANG_TYPE, QLANG_LIST_NAME)
        raise QlangError(m)
    return col


def get_translations(row, others, translations):
    these_translations = []
    for lang in others:
        try:
            lang_col = translations[lang]
            these_translations.append(row[lang_col])
        except KeyError:
            these_translations.append('')
    return these_translations


# throws errors: file not found (xlrd.open_workbook)
#                sheet not found (xlrd.sheet_by_name)
def translations_to_questionnaire(filename, prefix, suffix):
    first_part, second_part = os.path.split(filename)
    if not second_part.startswith(prefix):
        m = '"{}" does not start with supplied prefix "{}"'
        m = m.format(second_part, prefix)
        raise QlangError(m)
    orig_filename = os.path.join(first_part,second_part[len(prefix):])
    full_file, ext = os.path.splitext(orig_filename)
    dest_filename = full_file + suffix + ext
    with xlrd.open_workbook(filename) as book:
        with xlrd.open_workbook(orig_filename) as orig:
            trans_ws = book.sheet_by_name(QLANG_WORKSHEET_NAME)
            # Copy over "survey" and "choices" after merging translations
            survey_ws = orig.sheet_by_name(SURVEY)
            new_survey = get_worksheet_w_trans(survey_ws, trans_ws)
            choices_ws = orig.sheet_by_name(CHOICES)
            new_choices = get_worksheet_w_trans(choices_ws, trans_ws)
            wb = xlsxwriter.Workbook(dest_filename)
            survey_out_ws = wb.add_worksheet(SURVEY)
            write_out_worksheet(survey_out_ws, new_survey)
            choices_out_ws = wb.add_worksheet(CHOICES)
            write_out_worksheet(choices_out_ws, new_choices)
            # Copy all other sheets over
            for sheet in orig.sheet_names():
                if sheet not in (SURVEY, CHOICES):
                    rows = get_unicode_ws(orig.sheet_by_name(sheet))
                    this_ws = wb.add_worksheet(sheet)
                    write_out_worksheet(this_ws, rows)
            wb.close()
    m = 'Translations successfully merged: "{}"'.format(dest_filename)
    print(m)


def write_out_worksheet(ws, lines):
    for i, line in enumerate(lines):
        ws.write_row(i, 0, line)


# TODO does it work if there are no translation languages?
def get_worksheet_w_trans(ws, trans):
    # for each heading in built header, check if it exists in original header
    # then check if it is in translation file

    trans_rows = get_unicode_ws(trans)
    trans_header = trans_rows[0]
    ws_ind = trans_header.index(QLANG_WORKSHEET)
    row_ind = trans_header.index(QLANG_ROW)
    name_ind = trans_header.index(QLANG_NAME)
    column_ind = trans_header.index(QLANG_COLUMN)
    english_ind = trans_header.index(ENGLISH)
    trans_langs = trans_header[(english_ind + 1):]

    # Keep rows for this sheet
    ws_name = ws.name
    correct_trans_rows = [row for row in trans_rows if row[ws_ind] == ws_name]
    # Get this sheet
    ws_rows = get_unicode_ws(ws)
    ws_header = ws_rows[0]

    # dictionary: key is row, inside is another dictionary. key is column, and
    # value is text value
    # e.g. {1: {name: your_name, label::English: Name?, label::French: Nom?}}
    # except with quotes around the strings
    trans_dict = {}
    for row in correct_trans_rows:
        row_number = row[row_ind] - 1
        this_col = row[column_ind]
        this_dict = {}
        this_dict[QLANG_NAME] = row[name_ind]
        this_dict[BOTH_COL_FORMAT.format(this_col, ENGLISH)] = row[english_ind]
        for lang, val in zip(trans_langs, row[(english_ind+1):]):
            this_key = BOTH_COL_FORMAT.format(this_col, lang)
            this_dict[this_key] = val
        try:
            trans_dict[row_number].update(this_dict)
        except KeyError:
            trans_dict[row_number] = this_dict

    # BUILD header for survey, languages based on translation file
    combined_header = build_combined_header(ws_header, trans_langs)

    combined_lines = [combined_header]
    for i, line in enumerate(ws_rows):
        if i == 0:
            continue
        this_row = []
        for col in combined_header:
            orig = ''
            # see if original WS has column from combined header, then get val
            # for current row.
            try:
                orig_ind = ws_header.index(col)
                orig = line[orig_ind]
            except ValueError:
                pass
            # then see if there is corresponding value in translation lookup
            try:
                this_dict = trans_dict[i]
                new_val = this_dict[col]
                if col == QLANG_NAME and new_val != orig:
                    m = 'Name mismatch: {} <> {}'.format(orig, new_val)
                    raise QlangError(m)
                else:
                    orig = new_val
                if new_val == '':
                    m = '### Missing translation for row {} and col "{}"'
                    m = m.format(i + 1, col)
                    print(m)
            except (IndexError, KeyError) as e:
                pass
            this_row.append(orig)
        combined_lines.append(this_row)
    return combined_lines


def build_combined_header(ws_header, trans_langs):
    # need to know which are english columns
    # need to know which are translation columns
    # this probably could be optimized....
    combined_trans = []
    english_col = []
    for col in ws_header:
        if col.endswith(ENGLISH_SUFFIX):
            base = col[:-len(ENGLISH_SUFFIX)]
            english_col.append(base)
            for lang in trans_langs:
                new_col = BOTH_COL_FORMAT.format(base, lang)
                combined_trans.append(new_col)
    combined_header = []
    for col in ws_header:
        split_col = col.split(LANGUAGE_SEP)
        if split_col[0] not in english_col or split_col[1] == ENGLISH:
            combined_header.append(col)
    combined_header += combined_trans
    return combined_header


def get_unicode_ws(ws):
    rows = []
    for i in range(ws.nrows):
        this_row = ws.row(i)
        try:
            these_vales = [f(cell) for cell in this_row]
            rows.append(these_vales)
        except QlangError as e:
            m = 'Excel sheet "{}", row {}: {}'
            m.format(ws.name, i+1, e)
            raise QlangError(m)
    return rows

# important for switching between google docs and xlsx
def newline_space_fix(s):
    newline_space = '\n '
    fix = '\n'
    while newline_space in s:
        s = s.replace(newline_space, fix)
    return s


def space_newline_fix(s):
    space_newline = ' \n'
    fix = '\n'
    while space_newline in s:
        s = s.replace(space_newline, fix)
    return s


def f(cell):
    # Can format differently?
    if cell.ctype == xlrd.XL_CELL_BOOLEAN:
        return 'TRUE' if cell.value == 1 else 'FALSE'
    elif cell.ctype == xlrd.XL_CELL_EMPTY:
        return ''
    elif cell.ctype == xlrd.XL_CELL_TEXT:
        s = cell.value.strip()
        s = newline_space_fix(s)
        return s
    elif cell.ctype == xlrd.XL_CELL_NUMBER:
        return cell.value
    else:
        m = 'Bad cell type: {}. May be DATE'.format(cell.ctype)
        raise QlangError(m)
    return cell.value


if __name__ == '__main__':
    prog_desc = ('From an XLSForm create an MS-Excel file to facilitate quick '
                 'translation. Also, merge a translation file back into '
                 'XLSForm.')
    parser = argparse.ArgumentParser(description=prog_desc)

    file_help = 'One or more paths to files destined for conversion.'
    parser.add_argument('xlsxfile', nargs='+', help=file_help)

    merge_help = ('Include this flag to merge translation files back into '
                  'XLSForms. Do not include this flag to tell the program to '
                  'create translation files.')
    parser.add_argument('-m', '--merge', action='store_true',
                        help=merge_help)

    prefix_help = ('A prefix to prepend to the base file name.')
    parser.add_argument('-p', '--prefix', help=prefix_help)

    suffix_help = ('A suffix to add to the base file name. Cannot start with a '
                   'hyphen ("-").')
    parser.add_argument('-s', '--suffix', help=suffix_help)

    args = parser.parse_args()

    if args.suffix is None:
        args.suffix = QLANG_SUFFIX
    else:
        args.suffix = args.suffix.replace('%', '-')
    if args.prefix is None:
        args.prefix = QLANG_PREFIX
    else:
        args.prefix = args.prefix.replace('%', '-')

    for filename in set(args.xlsxfile):
        if args.merge:
            try:
                translations_to_questionnaire(filename, args.prefix,
                                              args.suffix)
            except FileNotFoundError as e:
                print(e)
        else:
            questionnaire_to_translations(filename, args.prefix)
