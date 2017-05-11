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
    parser.add_argument('-f', '--format', choices=('html', 'text', 'pdf'),
                        help=format_help)

    out_help = ('Path to write output. If this argument is not supplied, then '
                'STDOUT is used.')
    parser.add_argument('-o', '--outpath', help=out_help)

    args = parser.parse_args()

    s = ''
    odkform = Odkform(f=args.xlsxfile)
    if args.format == 'text':
        s = odkform.to_text(args.language)
    elif args.format == 'html' or not args.format:
        s = odkform.to_html(args.language)
        # Remove lines marked 'to-remove' this after using outpath instead. Try this example:
        # python3 -m pmix.ppp .dev/forms/FQ.xlsx > FQ.html
        d = odkform.to_dict(args.language)  # to-remove

        # <Testing>
        test = d['questions'][52]
        print(test)
        # odkform.render_html_output(test)
        # </Testing>

        odkform.render_html_output(d)  # to-remove
    if args.outpath:
        # TODO: Need to re-instate this after and use instead of render_html_output.
        with open(args.outpath, mode='w', encoding='utf-8') as f:
            f.write(s)
        pass
    else:
        print(s)
