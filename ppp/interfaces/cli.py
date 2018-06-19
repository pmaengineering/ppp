#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Command Line Interface."""
from argparse import ArgumentParser
from sys import stderr
from copy import copy

from ppp import run
from ppp.definitions.constants import SUPPORTED_FORMATS
from ppp.definitions.abstractions import chain
from ppp.definitions.error import OdkException, OdkFormError


def _required_fields(parser):
    """Add required fields to parser.

    Args:
        parser (ArgumentParser): Argparse object.

    Returns:
        ArgumentParser: Argeparse object.
    """
    # File
    #   type:'string'
    file_help = 'Path to source XLSForm(s).'
    parser.add_argument('xlsxfiles', nargs='+', help=file_help)
    # Bundled Option Presets
    #   type='single selection', options:'custom, developer/full, internal,
    #   public', default:'public'
    #   note='the CLI does not have 'custom'. Leaving this option blank in the
    #   CLI os the same as 'custom'.'
    presets_help = \
        ('Select from a preset of bundled options. The \'developer\' or '
         '\'full\' preset'
         ' renders a form that is the most similar to the original XlsForm. '
         'The \'internal\' preset is more human readable but is not stripped '
         'of sensitive information. The \'public\' option is like the '
         '\'internal\' optoin, only with sensitive information removed.')
    parser.add_argument('-p', '--preset', nargs='+',
                        choices=('public', 'internal', 'full', 'developer',
                                 'minimal'),
                        default='full', help=presets_help)
    return parser


def _non_preset_optional_fields(parser):
    """Add non-preset optional fields to parser.

    Args:
        parser (ArgumentParser): Argparse object.

    Returns:
        ArgumentParser: Argeparse object.
    """
    # Language
    #   type='single selection', default:''
    language_help = \
        ('Language to write the paper version in. If not specified, the '
         '\'default_language\' in the \'settings\' worksheet is used. If that '
         'is not specified and more than one language is in the XLSForm, the '
         'language that comes first alphabetically will be used.')
    parser.add_argument('-l', '--language', nargs='+', help=language_help)

    # Output Format
    #   type='single selection', default:'html'
    format_help = ('File format. HTML and DOC are supported formats. PDF is '
                   'not supported, but one can easily convert a PPP .doc file '
                   'into PDF via the use of WKHTMLtoPDF '
                   '(https://wkhtmltopdf.org/).')
    parser.add_argument('-f', '--format', nargs='+',
                        choices=SUPPORTED_FORMATS, default='doc',
                        help=format_help)
    return parser


def _preset_optional_fields(parser):
    """Add preset options to parser.

    These options are all boolean toggles. Their value should automatically
    update based on the bundle option preset selected. Also, they should either
    (a) greyed out unless the 'custom bundle option preset is selected, or (b)
    if a bundle option preset other than 'custom' is selected, the bundle
    option preset should automatically change to 'custom' if any of the
    options are changed.


    Args:
        parser (ArgumentParser): Argparse object.

    Returns:
        ArgumentParser: Argeparse object.
    """
    # TODO: Input replacement
    #   type='boolean', default:'TRUE if public else FALSE if internal else
    #   FALSE if developer/full'
    # input_replacement_help = \
    #     ('Adding this option will toggle replacement of visible choice '
    #      'options in input fields. Instead of the normal choice options, '
    #      'whatever has been placed in the \'ppp_input\' field of the XlsForm '
    #      'will be used. This is normally to hide sensitive information.')
    # parser.add_argument('-i', '--input-replacement', action='store_true',
    #                     help=input_replacement_help)

    # TODO: Exclusion
    #   type='boolean', default:'TRUE if public else FALSE if internal else
    #   FALSE if developer/full
    # exclusion_help = \
    #     ('Adding this option will toggle exclusion of certain survey form '
    #      'compoments from the rendered form. This can be used to remove '
    #      'ODK-specific implementation elements from the form which are only '
    #      'useful for developer, and can also be used to wholly remove '
    #      'sensitive information without any replacement.')
    # parser.add_argument('-e', '--exclusion', action='store_true',
    #                     help=exclusion_help)

    # TODO: Human-readable relevant text
    #   type='boolean', default:'TRUE if public else TRUE if internal else
    #   FALSE if developer/full
    # hr_relevant_help = \
    #     ('Adding this option will toggle display of human readable '
    #      '\'relevant\' text, rather than the syntax-heavy codified logic of '
    #      'the original XlsForm.')
    # parser.add_argument('-r', '--hr-relevant', action='store_true',
    #                     help=hr_relevant_help)

    # TODO: Human-readable constraint text
    #   type='boolean', default:'TRUE if public else FALSE if internal else
    #   FALSE if developer/full
    # hr_constraint_help = \
    #     ('Adding this option will toggle display of human readable '
    #      '\'constraint\' text, rather than the syntax-heavy codified logic of '
    #      'the original XlsForm.')
    # parser.add_argument('-c', '--hr-constraint', action='store_true',
    #                     help=hr_constraint_help)

    # TODO: No constraint text
    #   type='boolean', default:'FALSE if public else FALSE if internal
    #   else FALSE if developer/full
    # no_constraint_help = \
    #     ('Adding this option will toggle removal of all constraints from the '
    #      'rendered form.')
    # parser.add_argument('-C', '--no-constraint', action='store_true',
    #                     help=no_constraint_help)

    # TODO: General text replacements
    #   type='boolean', default:'TRUE if public else TRUE if internal else
    #   FALSE if developer/full
    # text_replacements_help = \
    #     ('Adding this option will toggle text replacements as shown in the '
    #      '\'text_replacements\' worksheet of the XlsForm. The most common '
    #      'function of text replacement is to render more human readable '
    #      'variable names, but can also be used to remove sensitive information'
    #      'or add brevity or clarity where needed.')
    # parser.add_argument('-t', '--text-replacements', action='store_true',
    #                     help=text_replacements_help)
    return parser


def _cli_only_fields(parser):
    """Add CLI-only fields to parser.

    Args:
        parser (ArgumentParser): Argparse object.

    Returns:
        ArgumentParser: Argeparse object.
    """
    debug_help = \
        'Turns on debug mode. Currently only works for \'html\' format. Only' \
        ' feature of debug mode currently is that it prints a stringified ' \
        'JSON representation of survey to the JavaScript console.'
    parser.add_argument('-d', '--debug', action='store_true', help=debug_help)

    # Survey Form Component Highlighting
    highlighting_help = 'Turns on highlighting of various portions of survey' \
                        ' components. Useful to assess positioning.'
    parser.add_argument('-H', '--highlight', action='store_true',
                        help=highlighting_help)

    # Out path
    out_help = ('Path (including file name) to save converted file if 1 file, '
                'else path to directory for multiple files, in which case file'
                ' names will be automatically generated.\n\nIf this argument '
                'is not supplied, then STDOUT is used.')
    parser.add_argument('-o', '--outpath', help=out_help)
    return parser


def _add_arguments(parser):
    """Add arguments to parser.

    Args:
        parser (ArgumentParser): Argparse object.

    Returns:
        ArgumentParser: Argeparse object.
    """
    return chain(parser, funcs=[_cli_only_fields, _non_preset_optional_fields,
                                _preset_optional_fields, _required_fields])


def cli():
    """Command line interface for package.

    Side Effects: Executes program.

    Command Syntax: python3 -m ppp <file> <options>

    Examples:
        # Creates a 'myFile.html' in English with component highlighting.
        python3 -m ppp myFile.xlsx -l 'English' -h > myFile.html
    """
    prog_desc = 'Convert XLSForm to Paper version.'

    argeparser = ArgumentParser(description=prog_desc)
    parser = _add_arguments(copy(argeparser))
    args = parser.parse_args()

    if args.highlight and args.format and args.format not in SUPPORTED_FORMATS:
        msg = 'Can only specify highlighting when using the following ' \
              'formats: \'html\', \'pdf\'.'
        raise OdkFormError(msg)

    try:
        run(files=list(args.xlsxfiles),
            languages=[l for l in args.language] if args.language else [None],
            format=args.format, outpath=args.outpath,
            debug=args.debug, highlight=args.highlight, preset=args.preset)
    except OdkException as err:
        err = 'An error occurred while attempting to convert \'{}\':\n{}'\
            .format(args.xlsxfiles, err)
        print(err, file=stderr)


if __name__ == '__main__':
    cli()
