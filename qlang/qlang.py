import os.path

import xlrd
import xlsxwriter


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


class QlangError(Exception):
    pass


def questionnaire_to_translations(filename, prefix):
    with xlrd.open_workbook(filename) as book:
        # TODO try - except with choices worksheet. possible not exists
        choices_ws = book.sheet_by_name(CHOICES)
        choices, c_others = process_worksheet(choices_ws)
        choices_dict = group_choices(choices)
        survey_ws = book.sheet_by_name(SURVEY)
        survey, s_others = process_worksheet(survey_ws)
        if set(c_others) != set(s_others):
            raise QlangError()
        write_out_translations(filename, prefix, c_others, survey, choices_dict)


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
    used_list_names = list(choices_dict.keys())
    for line in survey:
        out_row = [line[QLANG_WORKSHEET], line[QLANG_ROW] + 1,
                     line[QLANG_TYPE], line[QLANG_NAME], line[QLANG_COLUMN],
                     line[ENGLISH]]
        out_row += line[TRANSLATIONS]
        ws.write_row(n, 0, out_row)
        n += 1
        this_type = line[QLANG_TYPE].split(None)
        has_choice_list = this_type[0] in (SELECT_ONE, SELECT_MULTIPLE)
        if has_choice_list and this_type[1] in used_list_names:
            try:
                these_choices = choices_dict[this_type[1]]
                for c in these_choices:
                    choice_row = [c[QLANG_WORKSHEET], c[QLANG_ROW] + 1,
                                  c[QLANG_TYPE], c[QLANG_NAME],
                                  c[QLANG_COLUMN], c[ENGLISH]]
                    choice_row += c[TRANSLATIONS]
                    ws.write_row(n, 0, choice_row)
                    n += 1
                used_list_names.remove(this_type[1])
            except KeyError as e:
                # TODO make more informative message
                # don't terminate
                print(e)
    wb.close()
    print('### Unused list names in "{}"'.format(filename))
    for list_name in used_list_names:
        print(' - {}'.format(list_name))


def group_choices(choices):
    choices_dict = {}
    for line in choices:
        this_choice_list = line[QLANG_TYPE]
        if this_choice_list in choices_dict:
            choices_dict[this_choice_list].append(line)
        else:
            choices_dict[this_choice_list] = [line]
    return choices_dict


def preprocess_header(header):
    # list of tuples, index and column name, e.g. 'hint'
    english = []
    for i, cell in enumerate(header):
        # TODO check for string format, not empty string
        if cell.value.endswith(ENGLISH_SUFFIX):
            english.append((i, cell.value[:-len(ENGLISH_SUFFIX)]))
    if not english:
        raise QlangError()

    # by end of for-loop, should contain all the languages used in the header
    other_languages = set()
    # by end of for-loop, keys are columns with ::English. values are dicts
    # that have language and column
    translation_lookup = {}
    for i, column in english:
        prefix = COL_FORMAT.format(column)
        translations = [item for item in enumerate(header) if item[0] != i and
                        item[1].value.startswith(prefix)]
        these_languages = {lang.value[len(prefix):]: j for j, lang in
                           translations}
        translation_lookup[column] = these_languages
        other_languages |= set(these_languages.keys())
    others = list(other_languages)
    others.sort()
    return english, others, translation_lookup


def process_worksheet(worksheet):
    # Assumption that first row is the header
    header = worksheet.row(0)
    english, others, translations = preprocess_header(header)
    type_col = get_type_col(header)
    name_col = ([cell.value for cell in header]).index(QLANG_NAME)
    rows_for_output = []
    for i in range(worksheet.nrows):
        if i == 0:
            continue
        this_row = list(worksheet.row(i))
        # TODO error catching (index error)
        for j, column in english:
            this_cell = this_row[j]
            # No more blank values! Use '#####'
            if this_cell.value:
                this_dict = {}
                this_dict[QLANG_WORKSHEET] = worksheet.name
                this_dict[QLANG_ROW] = i
                this_dict[QLANG_TYPE] = this_row[type_col].value
                this_dict[QLANG_NAME] = this_row[name_col].value
                this_dict[QLANG_COLUMN] = column
                this_dict[ENGLISH] = this_cell.value
                this_dict[TRANSLATIONS] = get_translations(this_row, others,
                                                           translations[column])
                rows_for_output.append(this_dict)
    return rows_for_output, others


def get_type_col(header):
    headings = [cell.value for cell in header]
    if QLANG_TYPE in headings:
        col = headings.index(QLANG_TYPE)
    elif QLANG_LIST_NAME in headings:
        col = headings.index(QLANG_LIST_NAME)
    else:
        raise QlangError()
    return col


def get_translations(row, others, translations):
    these_translations = []
    for lang in others:
        try:
            lang_col = translations[lang]
            these_translations.append(row[lang_col].value)
        except KeyError:
            these_translations.append('')
    return these_translations


def translations_to_questionnaire(filename, prefix, suffix):
    first_part, second_part = os.path.split(filename)
    orig_filename = os.path.join(first_part,second_part[len(prefix):])
    full_file, ext = os.path.splitext(orig_filename)
    dest_filename = full_file + suffix + ext
    print("{} -> {}".format(filename, orig_filename))
    with xlrd.open_workbook(filename) as book:
        with xlrd.open_workbook(orig_filename) as orig:
            wb = xlsxwriter.Workbook(dest_filename)
            trans_ws = book.sheet_by_name(QLANG_WORKSHEET_NAME)
            survey_ws = orig.sheet_by_name(SURVEY)
            new_survey = get_worksheet_w_trans(survey_ws, trans_ws, SURVEY)
            survey_out_ws = wb.add_worksheet(SURVEY)
            write_out_worksheet(survey_out_ws, new_survey)
            choices_ws = orig.sheet_by_name(CHOICES)
            new_choices = get_worksheet_w_trans(choices_ws, trans_ws, CHOICES)
            choices_out_ws = wb.add_worksheet(CHOICES)
            write_out_worksheet(choices_out_ws, new_choices)
            settings_ws = orig.sheet_by_name(SETTINGS)
            new_settings = get_worksheet(settings_ws)
            settings_out_ws = wb.add_worksheet(SETTINGS)
            write_out_worksheet(settings_out_ws, new_settings)
            wb.close()


def write_out_worksheet(ws, lines):
    for i, line in enumerate(lines):
        ws.write_row(i, 0, line)

def get_worksheet_w_trans(ws, trans, ws_name):
    # for each heading in built header, check if it exists in original header
    # then check if it is in translation file

    trans_rows = get_worksheet(trans)
    trans_header = trans_rows[0]
    print(trans_header)
    ws_ind = trans_header.index(QLANG_WORKSHEET)
    row_ind = trans_header.index(QLANG_ROW)
    name_ind = trans_header.index(QLANG_NAME)
    column_ind = trans_header.index(QLANG_COLUMN)
    english_ind = trans_header.index(ENGLISH)
    trans_langs = trans_header[(english_ind + 1):]

    correct_trans_rows = [row for row in trans_rows if row[ws_ind] == ws_name]
    ws_rows = get_worksheet(ws)
    ws_header = ws_rows[0]

    # dictionary: key is row, inside is another dictionary. key is column, and
    # value is text value
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
            try:
                orig_ind = ws_header.index(col)
                orig = line[orig_ind]
            except ValueError:
                pass
            try:
                this_dict = trans_dict[i]
                new_val = this_dict[col]
                if col == QLANG_NAME and new_val != orig:
                    m = 'Name mismatch: {} <> {}'.format(orig, new_val)
                    raise QlangError(m)
                else:
                    orig = new_val
            except (IndexError, KeyError) as e:
                pass
            this_row.append(orig)
        combined_lines.append(this_row)
    return combined_lines


def build_combined_header(ws_header, trans_langs):
    # need to know which are english columns
    # need to know which are translation columns
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
    for i, col in enumerate(ws_header):
        split_col = col.split(LANGUAGE_SEP)
        if split_col[0] not in english_col or split_col[1] == ENGLISH:
            combined_header.append(col)
    combined_header += combined_trans
    return combined_header


def get_worksheet(ws):
    rows = []
    for i in range(ws.nrows):
        this_row = ws.row(i)
        these_vales = [f(cell) for cell in this_row]
        rows.append(these_vales)
    return rows


def f(cell):
    # Can format differently?
    if cell.ctype == xlrd.XL_CELL_BOOLEAN:
        return cell.value == 1
    elif cell.ctype == xlrd.XL_CELL_EMPTY:
        return ''
    elif cell.ctype == xlrd.XL_CELL_TEXT:
        return cell.value.strip()
    elif cell.ctype == xlrd.XL_CELL_NUMBER:
        return cell.value
    else:
        # TODO informative error messages here
        raise QlangError('Bad cell type: {}'.format(cell.ctype))
    return cell.value


if __name__ == '__main__':
    # filename = ['RJR1-Household-Questionnaire-v3-jkp.xlsx',
    #             'bootcamp_2.xlsx', 'RJR1-Listing-v3-jkp.xlsx',
    #             'RJR1-Household-Questionnaire-v3-jkp.xlsx',
    #             'RJR1-Female-Questionnaire-v3-jkp.xlsx',
    #             'RJR1-Reinterview-Questionnaire-v3-jkp.xlsx',
    #             'RJR1-SDP-Questionnaire-v3-jkp.xlsx',
    #             'RJR1-Selection-v3-jkp.xlsx']
    filename = [
        'PMARJ-FinalODKExam-RJ-v3-2016-02-11.xlsx',
        'PMARJ-Quiz1-ML-v2-2016-02-03-jkp.xlsx',
        'PMARJ-Quiz2-HQ-v4-2016-02-04-jkp.xlsx',
        'PMARJ-Quiz3-FQ-v2-2016-02-04-jkp.xlsx',
        'PMARJ-Quiz4-SDP-v3-2016-02-08.xlsx'
    ]
    prefix = QLANG_PREFIX
    suffix = QLANG_SUFFIX

    for i in filename:
        print(i)
        questionnaire_to_translations(i, prefix)

    # file_in = 'RJR1-SDP-Questionnaire-v6-jkp.xlsx'
    # file_out = 'qlang-RJR1-SDP-Questionnaire-v6-jkp.xlsx'
    # questionnaire_to_translations(file_in, prefix)
    # file_out = 'qlang-PMARJ-FinalODKExam-RJ-v2-2015.02.17.xlsx'
    # translations_to_questionnaire(file_out, prefix, suffix)

    #file_in = 'testqlang/PMARJ-Quiz2-HQ-v2-2016-02-04-jkp.xlsx'
    #questionnaire_to_translations(file_in, prefix)

    #file1 = 'testqlang/qlang-RJR1-Household-Questionnaire-v3-jkp.xlsx'
    #file1 = 'testqlang/qlang-RJR1-Female-Questionnaire-v3-jkp.xlsx'
    #translations_to_questionnaire(file1, prefix, suffix)

    # check for dups
    # translations_to_questionnaire(prefix+filename[1], prefix, suffix)
