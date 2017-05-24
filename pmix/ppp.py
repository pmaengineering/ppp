import argparse
from pmix.odkform import OdkForm
from pmix.error import OdkformError


if __name__ == '__main__':
    prog_desc = 'Convert XLSForm to Paper version.'
    parser = argparse.ArgumentParser(description=prog_desc)

    file_help = 'Path to source XLSForm.'
    parser.add_argument('xlsxfile', help=file_help)

    debug_help = 'Turns on debug mode. Currently only works for \'html\' format. Only feature of debug mode currently ' \
                 'is that it prints a stringified JSON representation of survey to the JavaScript console.'
    parser.add_argument('-d', '--debug', action='store_true', help=debug_help)

    highlighting_help = 'Turns on highlighting of various portions of survey components. Useful to assess positioning.'
    parser.add_argument('-hl', '--highlight', action='store_true', help=highlighting_help)

    language_help = 'Language to write the paper version in. If not specified, the \'default_language\' in the ' \
                    '\'settings\' worksheet is used. If that is not specified and more than one language is in the ' \
                    'Xlsform, the language that comes first alphabetically will be used.'
    parser.add_argument('-l', '--language', help=language_help)

    format_help = ('Format to generate. Currently "text" and "html" are supported. Future '
                   'formats include "pdf". If this flag is not supplied, output is html by default.')
    parser.add_argument('-f', '--format', choices=('html', 'text', 'dict', 'json', 'json_pretty', 'pdf'),
                        help=format_help)

    out_help = ('Path to write output. If this argument is not supplied, then '
                'STDOUT is used.')
    parser.add_argument('-o', '--outpath', help=out_help)

    args = parser.parse_args()

    if args.highlight and args.format and args.format not in ['html', 'pdf']:
        m = 'Can only specify highlighting when using the following formats: \'html\', \'pdf\'.'
        raise OdkformError(m)

    s = ''
    odkform = OdkForm(f=args.xlsxfile)
    if args.format == 'text':
        s = odkform.to_text(args.language)
    elif args.format == 'dict':
        s = odkform.to_dict(args.language)
    elif args.format == 'json':
        s = odkform.to_json(args.language, pretty=False)
    elif args.format == 'json_pretty':
        s = odkform.to_json(args.language, pretty=True)
    elif args.format == 'html' or not args.format:
        s = odkform.to_html(args.language, args.highlight, args.debug)
    if args.outpath:
        with open(args.outpath, mode='w', encoding='utf-8') as f:
            f.write(s)
    else:
        print(s)
