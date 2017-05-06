import argparse

try:
    from odkform import Odkform
    from ppp_render_html import render_html
except:
    try:
        from .odkform import Odkform
        from .ppp_render_html import render_html
    except:
        from pmix.odkform import Odkform
        from pmix.ppp_render_html import render_html

class OutputModeError(Exception):
    def __init__(self):
        print('Output Mode Error: Need to supply an output mode: text file, terminal, or HTML.')

def get_output_modes(args):
    output_modes = []
    if args.outpath:
        output_modes.append('text_file')
    elif args.toterminal:
        output_modes.append('terminal')
    elif not(args.nohtml):
        output_modes.append('html_file')
    return output_modes

if __name__ == '__main__':
    prog_desc = 'Convert XLSForm to Paper version.'
    parser = argparse.ArgumentParser(description=prog_desc)

    file_help = 'Path to source XLSForm.'
    parser.add_argument('xlsxfile', help=file_help)

    # Note: I believe this is currently disabled. To activate, add: action='store_true'.
    language_help = 'Language to write the paper version in.'
    parser.add_argument('-l', '--language', help=language_help)

    # Note: Temporarily disabled. Other form of mode input is being used.
    # format_help = ('Format to generate. Currently "text" is supported. Future '
    #                'formats include "html" and "pdf".')
    # parser.add_argument('-f', '--format', choices=('text', 'html', 'pdf'),
    #                     help=format_help)

    out_help = ('Path to write output. If this argument is not supplied, then '
                'STDOUT is used.')
    parser.add_argument('-o', '--outpath', action='store_true', help=out_help)

    toterminal_help = ('Prints output to terminal.')
    parser.add_argument('-t', '--toterminal', action='store_true', help=toterminal_help)

    nohtml_help = ('Option to refrain from generating HTML output.')
    parser.add_argument('-n', '--nohtml', action='store_true', help=nohtml_help)

    args = parser.parse_args()

    output_modes = get_output_modes(args)
    if len(output_modes) > 0:
        if ('terminal' or 'text_file') in output_modes:
            odkform = Odkform(of='plain_text', f=args.xlsxfile)
            s = odkform.to_text(args.language)
            if 'text_file' in output_modes:
                with open(args.outpath, mode='w', encoding='utf-8') as f:
                    f.write(s)
            elif 'terminal' in output_modes:
                print(s)
        elif 'html_file' in output_modes:
            odkform = Odkform(of='html', f=args.xlsxfile)
            html_questionnaire = odkform.to_html(args.language)
            # Testing
            print(html_questionnaire['questions'][50])
            render_html(html_questionnaire)
    else:
        raise OutputModeError
