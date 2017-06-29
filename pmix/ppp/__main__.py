#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CLI for PPP package."""
import sys
import argparse
from pmix.ppp.error import OdkException, OdkFormError
from pmix.ppp import run


def cli():
    """Command line interface for package."""
    prog_desc = 'Convert XLSForm to Paper version.'
    parser = argparse.ArgumentParser(description=prog_desc)

    file_help = 'Path to source XLSForm.'
    parser.add_argument('xlsxfile', help=file_help)

    debug_help = 'Turns on debug mode. Currently only works for \'html\' ' \
                 'format. Only feature of debug mode currently is that it ' \
                 'prints a stringified JSON representation of survey to the ' \
                 'JavaScript console.'
    parser.add_argument('-d', '--debug', action='store_true', help=debug_help)

    highlighting_help = 'Turns on highlighting of various portions of survey' \
                        ' components. Useful to assess positioning.'
    parser.add_argument('-H', '--highlight', action='store_true',
                        help=highlighting_help)

    language_help = 'Language to write the paper version in. If not ' \
                    'specified, the \'default_language\' in the \'settings\'' \
                    ' worksheet is used. If that is not specified and more' \
                    ' than one language is in the XLSForm, the language that' \
                    ' comes first alphabetically will be used.'
    parser.add_argument('-l', '--language', help=language_help)

    format_help = ('Format to generate. Currently "text" and "html" are '
                   'supported. Future formats include "pdf". If this flag is'
                   ' not supplied, output is html by default.')
    parser.add_argument('-f', '--format', choices=('html', 'text', 'pdf'),
                        default='html', const='html', nargs='?',
                        help=format_help)

    out_help = ('Path to write output. If this argument is not supplied, then '
                'STDOUT is used.')
    parser.add_argument('-o', '--outpath', help=out_help)

    args = parser.parse_args()

    if args.highlight and args.format and args.format not in ['html', 'pdf']:
        msg = 'Can only specify highlighting when using the following ' \
              'formats: \'html\', \'pdf\'.'
        raise OdkFormError(msg)

    try:
        run(in_file=args.xlsxfile, language=args.language,
            output_format=args.format, out_file=args.outpath,
            debug=args.debug, highlight=args.highlight)
    except OdkException as err:
        err = 'An error occurred while attempting to convert \'{}\':\n{}'\
            .format(args.xlsxfile, err)
        print(err, file=sys.stderr)
        print(err)


if __name__ == '__main__':
    cli()
