#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# The MIT License (MIT)
#
# Copyright (c) 2016 James K. Pringle
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


"""Build a translation file and use it

Supply source XLSForm(s) to build a translation file. Optionally supply an
XLSForm into which to merge translations. This file is a command-line tool.

Created: 3 October 2016
Last modified: 5 October 2016
Author: James K. Pringle
E-mail: jpringle@jhu.edu
"""

import argparse
import os.path

from verbiage import TranslationDict
import constants
import spreadsheet


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
        wb = spreadsheet.Workbook(args.merge)
        wb.merge_translations(translation_dict)
        outpath = get_wb_outpath(wb) if args.outpath is None else args.outpath
        wb.write_out(outpath)
        print('Merged translations into file: "{}"'.format(outpath))
