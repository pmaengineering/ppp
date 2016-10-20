#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Build a translation file and use it

Supply source XLSForm(s) to build a translation file. Optionally supply an
XLSForm into which to merge translations. This file is a command-line tool.

Example:

    $ python -m borrow.py *.xlsx

    Creates a translation file from all ".xlsx" files in the directory and
    writes it out to a new file.

    $ python -m borrow.py *.xlsx -m path/to/specific.xlsx

    Grabs all translations from all ".xlsx" files in the directory and uses
    them to translate path/to/specific.xlsx. Writes out the product to a new
    file.

Created: 3 October 2016
Last modified: 20 October 2016
Author: James K. Pringle
E-mail: jpringle@jhu.edu
"""

import argparse
import os.path

from verbiage import TranslationDict
import constants
import workbook


def translation_dict_from_files(files, ignore=None):
    result = TranslationDict()
    workbooks = [workbook.Workbook(f) for f in files]
    for wb in workbooks:
        this_dict = wb.create_translation_dict(ignore)
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

    merge_help = ('An XLSForm that receives the translations from source '
                  'files. If this argument is not supplied, then a translation '
                  'file is created.')
    parser.add_argument('-m', '--merge', help=merge_help)

    add_help = ('Add a language to the resulting output. The translation file '
                'will have a column for that language. Or, the merged XLSForm '
                'will include columns for that language and have translations '
                'for them if possible. This option can be supplied multiple '
                'times.')
    parser.add_argument('-a', '--add', action='append', help=add_help)

    ignore_help = ('A language to ignore when collecting and making '
                   'translations. This option can be supplied multiple times')
    parser.add_argument('-i', '--ignore', action='append', help=ignore_help)

    out_help = ('Path to write output. If this argument is not supplied, then '
                'defaults are used.')
    parser.add_argument('-o', '--outpath', help=out_help)

    args = parser.parse_args()
    ignore = set(args.ignore) if args.ignore else None
    add = set(args.add) if args.add else None

    translation_dict = translation_dict_from_files(set(args.xlsxfile),
                                                   ignore)
    if args.merge is None:
        outpath = constants.BORROW_OUT if args.outpath is None else args.outpath
        translation_dict.add_language(add)
        translation_dict.write_excel(outpath)
        print('Created translation file: "{}"'.format(outpath))
    else:
        wb = workbook.Workbook(args.merge)
        wb.add_language(add)
        wb.merge_translations(translation_dict, ignore)
        outpath = get_wb_outpath(wb) if args.outpath is None else args.outpath
        wb.write_out(outpath)
        print('Merged translations into file: "{}"'.format(outpath))
