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
from signal import signal, SIGPIPE, SIG_DFL

from pmix.ppp.definitions.error import OdkException, InvalidLanguageException
from pmix.ppp.odkform import OdkForm


def run(in_file, language=None, out_file=None, **kwargs):
    """Run ODK form conversion.

    Args:
        in_file (str): Path to load source file.
        language (str): Language to render form.
        output_format (str): File format to be output.
        out_file (str): Path to save converted file.
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
        output_format = kwargs['output_format']
        if output_format == 'text':
            output = form.to_text(lang=language, **kwargs)
        elif output_format in ('html', 'doc') or not output_format:
            output = form.to_html(lang=language, **kwargs)
        if out_file:
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
