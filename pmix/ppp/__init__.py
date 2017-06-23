#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A package for converting ODK forms."""
from pmix.ppp.odkform import OdkForm
from pmix.ppp.error import OdkFormError, OdkChoicesError, \
    InvalidLanguageException, AmbiguousLanguageError


def run(in_file, language=None, output_format=None, out_file=None,
        **kwargs):
    """Run ODK form conversion.

    Args:
        in_file (str): Path to load source file.
        output_format (str): File format to be output.
        out_file (str): Path to save converted file.
        **language (str): Language to render form.
        **debug (bool): Debugging on or off.
        **highlight (bool): Highlighting on or off.
    Raises:
        InvalidLanguageException: Language related.
        OdkChoicesError: Choice or choice list related.
        OdkFormError: General form related exception.
    """
    form = OdkForm(file=in_file)
    try:
        output = None
        if output_format == 'text':
            output = form.to_text(**kwargs)
        elif output_format == 'html' or not output_format:
            output = form.to_html(**kwargs)
        if out_file:
            with open(out_file, mode='w', encoding='utf-8') as file:
                file.write(output)
        else:
            print(output)
    except InvalidLanguageException as err:
        if len(str(err)) > 0:
            raise InvalidLanguageException(err)
        elif language is None:
            msg = 'InvalidLanguageException: An unknown error occurred when ' \
                  'attempting to convert form. If a language was not ' \
                  'supplied, please supply and try again.'
            raise InvalidLanguageException(msg)
        elif language not in form.languages:
            msg = 'Specified language not found in form: ' + language
            msg += '\n\nThe form \'{}\' contains the following languages' \
                   '.\n'.format(in_file)
            for lang in form.languages:
                msg += '  * ' + lang + '\n'
            raise InvalidLanguageException(msg[0:-1])
    except AmbiguousLanguageError as err:
        raise AmbiguousLanguageError(err)
    except OdkChoicesError as err:
        raise OdkChoicesError(err)
    except OdkFormError as err:
        raise OdkFormError(err)
