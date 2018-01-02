#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
About PPP
PPP is a tool that converts ODK XlsForm specification .xlsx Excel files to more
human-readable, printable formats, commonly called "paper questionnaires".

Officially, PPP stands for "Pretty PDF Printer", but other formats are
supported (see: the `--format` option described in the "CLI How-to").

PPP Web Application
- Convert XlsForms online: http://ppp.pma2020.org
- Github: https://github.com/pma-2020/ppp-web

Functions
- run: Common executional entry point from interfaces.
"""
import os
from signal import signal, SIGPIPE, SIG_DFL

from pmix.ppp.definitions.error import OdkException, InvalidLanguageException
from pmix.ppp.odkform import OdkForm


def convert_file(in_file, language=None, outpath=None, **kwargs):
    """Run ODK form conversion.

    Args:
        in_file (str): Path to load source file.
        language (str or None): Language to render form.
        output_format (str): File format to be output.
        outpath (str or None): Path to save converted file.
        **debug (bool): Debugging on or off.
        **highlight (bool): Highlighting on or off.

    Raises:
        InvalidLanguageException: Language related.
        OdkChoicesError: Choice or choice list related.
        OdkFormError: General form related exception.
    """
    form = OdkForm.from_file(in_file)

    try:
        output = None
        output_format = \
            kwargs['output_format'] if 'output_format' in kwargs else 'html'
        if output_format == 'text':
            output = form.to_text(lang=language, **kwargs)
        elif output_format in ('html', 'doc'):
            output = form.to_html(lang=language, **kwargs)

        if outpath:
            if os.path.isdir(outpath) and not os.path.exists(outpath):
                os.makedirs(outpath)
            if os.path.isdir(outpath):
                base_filename =  os.path.basename(os.path.splitext(in_file)[0])
                lang = '-' + language if language else ''
                options_affix = '-' + kwargs['preset'] \
                    if 'preset' in kwargs and kwargs['preset'] != 'developer' \
                    else ''
                out_file = outpath + base_filename + lang + options_affix + \
                           '.' + output_format
            else:
                out_file = outpath
            with open(out_file, mode='w', encoding='utf-8') as file:
                file.write(output)
        else:
            try:
                print(output)
            except BrokenPipeError:  # If output is piped.
                signal(SIGPIPE, SIG_DFL)
                print(output)
    except InvalidLanguageException as err:
        if str(err):
            raise InvalidLanguageException(err)
        elif language is None:
            msg = 'InvalidLanguageException: An unknown error occurred when ' \
                  'attempting to convert form. If a language was not ' \
                  'supplied, please supply and try again.'
            raise InvalidLanguageException(msg)
    except OdkException as err:
        raise OdkException(err)


def run(files, languages=[None], outpath=None, **kwargs):
    """Run ODK form conversion on n files of n option combinations.

    Args:
        files (list): Path to load source file.
        languages (list): Languages to render forms.
        output_format (str): File format to be output.
        outpath (str): Path of file name to save converted file if 1 file,
            else path to directory for multiple files, in which case file names
            will be automatically generated.
        **debug (bool): Debugging on or off.
        **highlight (bool): Highlighting on or off.
    """
    _outpath = outpath
    for file in files:
        if len(files) > 1 and not outpath:
            _outpath = os.path.dirname(file) + '/'
            # print(_outpath)
        for language in languages:
            # TODO: 2017.11.27-jef: Add 'n option combo' functionality.

            convert_file(file, language, outpath=_outpath, **kwargs)
