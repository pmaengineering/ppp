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
Last modified: 5 October 2016
Author: James K. Pringle
E-mail: jpringle@jhu.edu
"""

import argparse
import os.path

from verbiage import TranslationDict
import constants
import workbook


def translation_dict_from_files(files):
    result = TranslationDict()
    workbooks = [workbook.Workbook(f) for f in files]
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

    merge_help = ('An XLSForm that receives the translations from source '
                  'files. If this argument is not supplied, then a translation '
                  'file is created.')
    parser.add_argument('-m', '--merge', help=merge_help)

    out_help = ('Path to write output. If this argument is not supplied, then '
                'defaults are used.')
    parser.add_argument('-o', '--outpath', help=out_help)

    args = parser.parse_args()

    translation_dict = translation_dict_from_files(set(args.xlsxfile))
    if args.merge is None:
        outpath = constants.BORROW_OUT if args.outpath is None else args.outpath
        translation_dict.write_out(outpath)
        print('Created translation file: "{}"'.format(outpath))
    else:
        wb = workbook.Workbook(args.merge)
        wb.merge_translations(translation_dict)
        outpath = get_wb_outpath(wb) if args.outpath is None else args.outpath
        wb.write_out(outpath)
        print('Merged translations into file: "{}"'.format(outpath))
