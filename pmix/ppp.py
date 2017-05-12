import argparse
from pmix.odkform import Odkform


if __name__ == '__main__':
    prog_desc = 'Convert XLSForm to Paper version.'
    parser = argparse.ArgumentParser(description=prog_desc)

    file_help = 'Path to source XLSForm.'
    parser.add_argument('xlsxfile', help=file_help)

    language_help = 'Language to write the paper version in.'
    parser.add_argument('-l', '--language', help=language_help)

    format_help = ('Format to generate. Currently "text" and "html" are supported. Future '
                   'formats include "pdf". If this flag is not supplied, output is html by default.')
    parser.add_argument('-f', '--format', choices=('html', 'text', 'json', 'pdf'),
                        help=format_help)

    out_help = ('Path to write output. If this argument is not supplied, then '
                'STDOUT is used.')
    parser.add_argument('-o', '--outpath', help=out_help)

    args = parser.parse_args()

    s = ''
    odkform = Odkform(f=args.xlsxfile)
    if args.format == 'text':
        s = odkform.to_text(args.language)
    elif args.format == 'json':
        s = odkform.to_json(args.language)
    elif args.format == 'html' or not args.format:
        s = odkform.to_html(args.language)
    if args.outpath:
        with open(args.outpath, mode='w', encoding='utf-8') as f:
            f.write(s)
    else:
        print(s)
