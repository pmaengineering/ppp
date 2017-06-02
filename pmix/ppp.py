"""CLI for PPP package."""
import argparse
from pmix.odkform import OdkForm
from pmix.error import OdkformError


if __name__ == '__main__':
    PROG_DESC = 'Convert XLSForm to Paper version.'
    PARSER = argparse.ArgumentParser(description=PROG_DESC)

    FILE_HELP = 'Path to source XLSForm.'
    PARSER.add_argument('xlsxfile', help=FILE_HELP)

    DEBUG_HELP = 'Turns on debug mode. Currently only works for \'html\' ' \
                 'format. Only feature of debug mode currently is that it ' \
                 'prints a stringified JSON representation of survey to the ' \
                 'JavaScript console.'
    PARSER.add_argument('-d', '--debug', action='store_true', help=DEBUG_HELP)

    HIGHLIGHTING_HELP = 'Turns on highlighting of various portions of survey' \
                        ' components. Useful to assess positioning.'
    PARSER.add_argument('-hl', '--highlight', action='store_true',
                        help=HIGHLIGHTING_HELP)

    LANGUAGE_HELP = 'Language to write the paper version in. If not ' \
                    'specified, the \'default_language\' in the \'settings\'' \
                    ' worksheet is used. If that is not specified and more' \
                    ' than one language is in the Xlsform, the language that' \
                    ' comes first alphabetically will be used.'
    PARSER.add_argument('-l', '--language', help=LANGUAGE_HELP)

    FORMAT_HELP = ('Format to generate. Currently "text" and "html" are '
                   'supported. Future formats include "pdf". If this flag is'
                   ' not supplied, output is html by default.')
    PARSER.add_argument('-f', '--format', choices=('html', 'text', 'dict',
                                                   'json', 'json_pretty',
                                                   'pdf'),
                        help=FORMAT_HELP)

    OUT_HELP = ('Path to write output. If this argument is not supplied, then '
                'STDOUT is used.')
    PARSER.add_argument('-o', '--outpath', help=OUT_HELP)

    ARGS = PARSER.parse_args()

    if ARGS.highlight and ARGS.format and ARGS.format not in ['html', 'pdf']:
        M = 'Can only specify highlighting when using the following formats:' \
            ' \'html\', \'pdf\'.'
        raise OdkformError(M)

    S = None
    ODKFORM = OdkForm(file=ARGS.xlsxfile)
    if ARGS.format == 'text':
        S = ODKFORM.to_text(ARGS.language)
    elif ARGS.format == 'dict':
        S = ODKFORM.to_dict(ARGS.language)
    elif ARGS.format == 'json':
        # pylint: disable=redefined-variable-type
        S = ODKFORM.to_json(ARGS.language, pretty=False)
    elif ARGS.format == 'json_pretty':
        S = ODKFORM.to_json(ARGS.language, pretty=True)
    elif ARGS.format == 'html' or not ARGS.format:
        S = ODKFORM.to_html(ARGS.language, ARGS.highlight, ARGS.debug)
    if ARGS.outpath:
        with open(ARGS.outpath, mode='w', encoding='utf-8') as f:
            f.write(S)
    else:
        print(S)
