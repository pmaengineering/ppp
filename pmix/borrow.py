#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Build a translation file and use it.

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

from pmix.verbiage import TranslationDict
from pmix.xlsform import Xlsform


def borrow_cli():  # pylint: disable=too-many-locals
    """Run the CLI for this module."""
    prog_desc = 'Grab translations from existing XLSForms'
    parser = argparse.ArgumentParser(description=prog_desc)

    file_help = 'One or more paths to source XLSForms containing translations.'
    parser.add_argument('xlsxfile', nargs='+', help=file_help)

    merge_help = ('An XLSForm that receives the translations from source '
                  'files. If this argument is not supplied, then a '
                  'translation file is created.')
    parser.add_argument('-m', '--merge', help=merge_help)

    correct_help = ('Mark a given file as correct. Text from these files will '
                    'disallow diverse translations from files not marked as '
                    'correct. This is a way to give files precedence for '
                    'translations.')
    parser.add_argument('-C', '--correct', action='append', help=correct_help)

    no_diverse_help = 'If text has diverse translations, do not borrow it.'
    parser.add_argument('-D', '--no_diverse', action='store_true',
                        help=no_diverse_help)

    diverse_help = ('Supply a language. Used without the --merge argument, '
                    'this creates a worksheet that shows only strings with '
                    'diverse translations for the supplied language.')
    parser.add_argument('-d', '--diverse', help=diverse_help)

    add_help = ('Add a language to the resulting output. The translation file '
                'will have a column for that language. Or, the merged XLSForm '
                'will include columns for that language and have translations '
                'for them if possible. This option can be supplied multiple '
                'times.')
    parser.add_argument('-a', '--add', action='append', help=add_help)

    ignore_help = ('A language to ignore when collecting and making '
                   'translations. This option can be supplied multiple times')
    parser.add_argument('-i', '--ignore', action='append', help=ignore_help)

    carry_help = ('If translations are missing, carry over the same text from '
                  'the source language. The default is to leave missing.')
    parser.add_argument('-c', '--carry', action='store_true', help=carry_help)

    out_help = ('Path to write output. If this argument is not supplied, then '
                'defaults are used.')
    parser.add_argument('-o', '--outpath', help=out_help)

    args = parser.parse_args()
    ignore = set(args.ignore) if args.ignore else None
    add = sorted(list(set(args.add))) if args.add else None

    translation_dict = TranslationDict()
    extracted = set()
    if args.correct:
        for path in args.correct:
            if path in extracted:
                continue
            xlsform = Xlsform(path)
            translation_dict.extract_translations(xlsform, correct=True)
            extracted.add(path)
    for path in args.xlsxfile:
        if path in extracted:
            continue
        xlsform = Xlsform(path)
        translation_dict.extract_translations(xlsform)
        extracted.add(path)

    if args.merge is None:
        outpath = 'translations.xlsx' if args.outpath is None else args.outpath
        if args.diverse:
            translation_dict.write_diverse_excel(outpath, args.diverse)
        else:
            translation_dict.write_excel(outpath, add)
        print('Created translation file: "{}"'.format(outpath))
    else:
        xlsform = Xlsform(args.merge)
        # wb.add_language(add)
        xlsform.merge_translations(translation_dict, ignore, carry=args.carry,
                                   no_diverse=args.no_diverse)
        outpath = args.outpath
        if outpath is None:
            orig = xlsform.file
            base, ext = os.path.splitext(orig)
            outpath = ''.join((base, '-borrow', ext))
        xlsform.write_out(outpath)
        print('Merged translations into file: "{}"'.format(outpath))


if __name__ == '__main__':
    borrow_cli()
