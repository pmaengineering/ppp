#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# The MIT License (MIT)
#
# Copyright (c) 2016 PMA2020
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

"""

Author: James K. Pringle
E-mail: jpringle@jhu.edu
Last-modified: 9 March 2017
"""

# from builtins import str
import argparse
try:
    from scan_constants import SUFFIX, PREEXISTING, PMA, CHECK_VERSIONING, STRICT_LINKING, VALIDATE, EXTRAS, DEBUG
except:
    from .scan_constants import SUFFIX, PREEXISTING, PMA, CHECK_VERSIONING, STRICT_LINKING, VALIDATE, EXTRAS, DEBUG


def command_line_interface():
    prog_desc = ('Convert files from XLSForm to XForm and validate. '
                 'This versatile program can accept .xls or .xlsx files as '
                 'input. The output is a pretty-formatted XML file. An '
                 'attempt is made to use the ODKValidate JAR file to analyze '
                 'the result--Java is required for success. The program '
                 'default is to enforce PMA2020 conventions for file naming '
                 'and linking. However, this can be turned off to convert any '
                 'XLSForm to XForm for use in ODK.')
    parser = argparse.ArgumentParser(description=prog_desc)

    file_help = 'One or more paths to files destined for conversion.'
    parser.add_argument('xlsxfile', nargs='+', help=file_help)

    reg_help = ('This flag indicates the program should convert to XForm and '
                'not try to make PMA2020-specific edits.')
    parser.add_argument('-r', '--regular', action='store_true', help=reg_help)

    ignore_version_help = ('Ignore versioning in filename, form_id, '
                           'form_title, and save_form. In other words, the '
                           'default (without this flag) is to ensure '
                           'version consistency.')
    parser.add_argument('-i', '--ignore_version', action='store_true',
                        help=ignore_version_help)

    linking_warn_help = ('Produce warnings for incorrect linking directives. '
                         'Default is to raise an exception and halt the '
                         'program')
    parser.add_argument('-l', '--linking_warn', action='store_true',
                        help=linking_warn_help)

    extras_help = 'Do not perform extra checks'
    parser.add_argument('-E', '--no_extras', action='store_true', help=extras_help)

    noval_help = 'Do not validate XML output with ODK Validate.'
    parser.add_argument('-n', '--no_validate', action='store_true',
                        help=noval_help)

    overwrite_help = ('Include this flag to prevent overwriting '
                      'pre-existing files.')
    parser.add_argument('-p', '--preexisting', action='store_true',
                        help=overwrite_help)

    suffix_help = ('A suffix to add to the base file name. Cannot start with a '
                   'hyphen ("-").')
    parser.add_argument('-s', '--suffix', help=suffix_help)

    debug_help = 'Show debug information. Helpful for squashing bugs.'
    parser.add_argument('-d', '--debug', action='store_true', help=debug_help)

    args = parser.parse_args()

    xlsxfiles = [str(filename) for filename in args.xlsxfile]
    if args.suffix is None:
        suffix = u''
    else:
        suffix = str(args.suffix)
    check_versioning = not args.ignore_version
    pma = not args.regular
    strict_linking = not args.linking_warn
    validate = not args.no_validate
    extras = not args.no_extras

    kwargs = {
        SUFFIX: suffix,
        PREEXISTING: args.preexisting,
        PMA: pma,
        CHECK_VERSIONING: check_versioning,
        STRICT_LINKING: strict_linking,
        VALIDATE: validate,
        EXTRAS: extras,
        DEBUG: args.debug
    }

    return xlsxfiles, kwargs
