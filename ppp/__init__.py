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
from copy import copy
try:
    # noinspection PyUnresolvedReferences
    from signal import signal, SIGPIPE, SIG_DFL
except ImportError as e:
    pass
from itertools import product
from collections import OrderedDict

from ppp.definitions.error import OdkException, InvalidLanguageException
from ppp.definitions.constants import MULTI_ARGUMENT_CONVERSION_OPTIONS
from ppp.odkform import OdkForm


def convert_file(in_file, language=None, outpath=None, **kwargs):
    """Run ODK form conversion.

    Args:
        in_file (str): Path to load source file.
        language (str or None): Language to render form.
        outpath (str or None): Path to save converted file.
        **format (str): File format to be output.
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
            kwargs['format'] if 'format' in kwargs else 'html'
        if output_format == 'text':
            output = form.to_text(lang=language, **kwargs)

        elif output_format in ('html', 'doc'):
            output = form.to_html(lang=language, **kwargs)

        if outpath:
            if os.path.isdir(outpath) and not os.path.exists(outpath):
                os.makedirs(outpath)
            if os.path.isdir(outpath):
                base_filename = os.path.basename(os.path.splitext(in_file)[0])
                lang = '-' + language if language else ''
                options_affix = '-' + kwargs['preset'] \
                    if 'preset' in kwargs and kwargs['preset'] != 'developer' \
                    else ''
                out_file = '{}{}{}{}.{}'.format(outpath, base_filename, lang,
                                                options_affix, output_format)

                if isinstance(out_file, list):
                    if out_file[0] == '/':
                        out_file = out_file[1:]
            else:
                out_file = outpath
            with open(out_file, mode='w', encoding='utf-8') as file:
                file.write(output)
            print(out_file)
        else:
            try:
                print(output)
            except BrokenPipeError:  # If output is piped.
                try:
                    signal(SIGPIPE, SIG_DFL)
                # noinspection PyBroadException
                except:
                    pass
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


def enumerate_combos(dict_with_lists):
    """Enumerate keyword-arg combination variants.

    Args:
        dict_with_lists (dict): A dictionary of lists.

    Returns:
        list: A list of dicts, where each list in dict_of_lists has been
        de-listed to a single value.
    """
    dict_with_only_lists = \
        OrderedDict({k: v for k, v in dict_with_lists.items()
                     if isinstance(v, list)})
    dict_without_lists = \
        {k: v for k, v in dict_with_lists.items() if not isinstance(v, list)}

    ds1 = dict_with_only_lists.values()
    ds2 = [i for i in ds1]
    ds3 = list(product(*ds2))
    ds4 = [dict(zip(dict_with_only_lists, i)) for i in ds3]
    full_dict_combos = [{**i, **dict_without_lists} for i in ds4]

    return full_dict_combos


def num_args(option):
    """Get number of args, aka "nargs" for a given option."""
    return len(option) if isinstance(option, list) else 1


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
    _kwargs = copy(kwargs)
    combos = enumerate_combos(_kwargs)
    num_output = num_args(files) * num_args(languages) * num_args(combos)

    if num_output > 1 or outpath:
        print('Creating files.')

    for file in files:
        if num_output > 1 and not outpath:
            _outpath = os.path.dirname(file) + '/'
        for language in languages:
            for combo in combos:
                convert_file(file, language, outpath=_outpath, **combo)
