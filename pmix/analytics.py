"""

Get the R code for PMA Analytics

Need to be able to get the ODK names from files (possibly collapse across groups)

"""


import argparse

from pmix.workbook import Workbook
from pmix import constants


def is_analytics_type(type):
    bad_types = (
        constants.ODK_CALCULATE,
        constants.ODK_HIDDEN,
        constants.BEGIN_START,
        constants.END_START,
        constants.ODK_START,
        constants.ODK_END,
        constants.ODK_DEVICE,
        constants.ODK_SIM,
        constants.ODK_PHONE
    )
    bad = any((type.startswith(bad) for bad in bad_types))
    return not bad and type != ""


def get_filtered_survey_names(xlsxfiles):
    results = {}
    for f in set(xlsxfiles):
        wb = Workbook(f)
        form_id = wb.get_form_id()
        type = wb[constants.SURVEY].column(constants.QLANG_TYPE)
        name = wb[constants.SURVEY].column(constants.QLANG_NAME)
        names = [n for t, n in zip(type, name) if is_analytics_type(t)]
        results[form_id] = names
    return results


def format_dict_for_analytics(filtered_results):
    for k in filtered_results:
        first_line = '"{}" = c('.format(k)
        v = filtered_results[k]
        entries = ['    "{}"'.format(entry) for entry in v]
        inner = ",\n".join(entries)
        last_line = ')'
        return "\n".join([first_line, inner, last_line])


def send_analytics_code(xlsxfiles):
    results = get_filtered_survey_names(xlsxfiles)
    string = format_dict_for_analytics(results)
    print(string)


if __name__ == '__main__':
    prog_desc = 'Help facilitate analytics by extracting useful information'
    parser = argparse.ArgumentParser(description=prog_desc)

    file_help = 'One or more paths to source XLSForms.'
    parser.add_argument('xlsxfile', nargs='+', help=file_help)

    args = parser.parse_args()

    send_analytics_code(args.xlsxfile)
