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

    # # I. Required Fields # #
    # I.A. File
    #     type:'string'
    file_help = 'Path to source XLSForm.'
    parser.add_argument('xlsxfile', help=file_help)
    # I.B. Bundled Option Presets
    #     type:'single selection', options:'custom, developer, internal,
    #     public', default:'public', note:'the CLI does not have 'custom'.
    #     Leaving this option blank in the CLI os the same as 'custom'.'
    presets_help = \
        ('Select from a preset of bundled options. The \'developer\' preset'
         ' renders a form that is the most similar to the original XlsForm. '
         'The \'internal\' preset is more human readable but is not stripped '
         'of sensitive information. The \'public\' option is like the '
         '\'internal\' optoin, only with sensitive information removed.')
    parser.add_argument('-p', '--preset',
                        choices=('public', 'internal', 'developer'),
                        default='developer', const='developer', nargs='?',
                        help=presets_help)


    # # II. Optional Fields # #
    # - II.A. Non-bundled options
    # II.A.1. Language
    #     type:'single selection', default:''
    language_help = \
        ('Language to write the paper version in. If not specified, the '
         '\'default_language\' in the \'settings\' worksheet is used. If that '
         'is not specified and more than one language is in the XLSForm, the '
         'language that comes first alphabetically will be used.')
    parser.add_argument('-l', '--language', help=language_help)

    # II.A.2. Output Format
    #     type='single selection', default:'pdf'
    format_help = ('Format to generate. Currently "text" and "html" are '
                   'supported. Future formats include "pdf". If this flag is'
                   ' not supplied, output is html by default.')
    parser.add_argument('-f', '--format',
                        choices=('html', 'text', 'pdf', 'doc'), # TODO: doc.
                        default='html', const='html', nargs='?',
                        help=format_help)


    # - II.B. Bundled options
    #     note:'These options are all boolean toggles. Their value
    #     should automatically update based on the bundle option preset
    #     selected. Also, they should either (a) greyed out unless the 'custom'
    #     bundle option preset is selected, or (b) if a bundle option preset
    #     other than 'custom' is selected, the bundle option preset should
    #     automatically change to 'custom' if any of the options are changed.'
    # II.B.1 Input replacement
    #     type='boolean', default:'TRUE if public else FALSE if internal else
    #     FALSE if developer'
    input_replacement_help = \
        ('Adding this option will toggle replacement of visible choice '
        'options in input fields. Instead of the normal choice options, '
        'whatever has been placed in the \'ppp_input\' field of the XlsForm '
        'will be used. This is normally to hide sensitive information.')
    parser.add_argument('-i', '--input-replacement', action='store_true',
                        help=input_replacement_help)

    # II.B.1 Exclusion
    #     type='boolean', default:'TRUE if public else FALSE if internal else
    #     FALSE if developer
    exclusion_help = \
        ('Adding this option will toggle exclusion of certain survey form '
         'compoments from the rendered form. This can be used to remove '
         'ODK-specific implementation elements from the form which are only '
         'useful for developers, and can also be used to wholly remove '
         'sensitive information without any replacement.')
    parser.add_argument('-e', '--exclusion', action='store_true',
                        help=exclusion_help)

    # II.B.1 Human-readable relevant text
    #     type='boolean', default:'TRUE if public else TRUE if internal else
    #     FALSE if developer
    hr_relevant_help = \
        ('Adding this option will toggle display of human readable '
         '\'relevant\' text, rather than the syntax-heavy codified logic of '
         'the original XlsForm.')
    parser.add_argument('-r', '--hr-relevant', action='store_true',
                        help=hr_relevant_help)

    # II.B.1 Human-readable constraint text
    #     type='boolean', default:'TRUE if public else FALSE if internal else
    #     FALSE if developer
    hr_constraint_help = \
        ('Adding this option will toggle display of human readable '
         '\'constraint\' text, rather than the syntax-heavy codified logic of '
         'the original XlsForm.')
    parser.add_argument('-c', '--hr-constraint', action='store_true',
                        help=hr_constraint_help)

    # II.B.1 No constraint text
    #     type='boolean', default:'FALSE if public else FALSE if internal else
    #     FALSE if developer
    no_constraint_help = \
        ('Adding this option will toggle removal of all constraints from the '
         'rendered form.')
    parser.add_argument('-C', '--no-constraint', action='store_true',
                        help=no_constraint_help)

    # II.B.1 General text replacements
    #     type='boolean', default:'TRUE if public else TRUE if internal else
    #     FALSE if developer
    text_replacements_help = \
        ('Adding this option will toggle text replacements as shown in the '
         '\'text_replacements\' worksheet of the XlsForm. The most common '
         'function of text replacement is to render more human readable '
         'variable names, but can also be used to remove sensitive information'
         'or add brevity or clarity where needed.')
    parser.add_argument('-t', '--text-replacements', action='store_true',
                        help=text_replacements_help)


    # - II.C. CLI-only
    # II.C.1. Debug
    debug_help = \
        'Turns on debug mode. Currently only works for \'html\' format. Only' \
        ' feature of debug mode currently is that it prints a stringified ' \
        'JSON representation of survey to the JavaScript console.'
    parser.add_argument('-d', '--debug', action='store_true', help=debug_help)

    # II.C.2. Component Highlighting
    highlighting_help = 'Turns on highlighting of various portions of survey' \
                        ' components. Useful to assess positioning.'
    parser.add_argument('-H', '--highlight', action='store_true',
                        help=highlighting_help)

    # II.C.3. Out path
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


if __name__ == '__main__':
    cli()
