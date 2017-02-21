import argparse

from pmix.odkform import Odkform


if __name__ == '__main__':
    prog_desc = 'Convert XLSForm to Paper version.'
    parser = argparse.ArgumentParser(description=prog_desc)

    file_help = 'Path to source XLSForm.'
    parser.add_argument('xlsxfile', help=file_help)

    language_help = 'Language to write the paper version in.'
    parser.add_argument('-l', '--language', help=language_help)

    format_help = ('Format to generate. Currently "text" is supported. Future '
                   'formats include "html" and "pdf".')
    parser.add_argument('-f', '--format', choices=('text', 'html', 'pdf'),
                        help=format_help)

    out_help = ('Path to write output. If this argument is not supplied, then '
                'STDOUT is used.')
    parser.add_argument('-o', '--outpath', help=out_help)

    args = parser.parse_args()

    odkform = Odkform(f=args.xlsxfile)

    s = odkform.to_text(args.language)

    if args.outpath:
        with open(args.outpath, mode='w') as f:
            f.write(s)
    else:
        print(s)
