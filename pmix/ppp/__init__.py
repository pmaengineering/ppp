#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A package for converting ODK forms."""
from pmix.ppp.odkform import OdkForm
from pmix.ppp.error import OdkFormError, OdkChoicesError, \
    InvalidLanguageException


def run(inpath, language, output_format, outfile, **kwargs):
    """Run ODK form conversion.

    Args:
        inpath (str): Path to load source file.
        language (str): Language to render form.
        output_format (str): File format to be output.
        outfile (str): Path to save converted file.
        **debug (bool): Debugging on or off.
        **highlight (bool): Highlighting on or off.
    Raises:
        InvalidLanguageException: Language related.
        OdkChoicesError: Choice or choice list related.
        OdkFormError: General form related exception.
    """
    try:
        form = OdkForm(file=inpath)
        output = None
        if output_format == 'text':
            output = form.to_text(language)
        elif output_format == 'html' or not output_format:
            output = form.to_html(language, **kwargs)
        if outfile:
            with open(outfile, mode='w', encoding='utf-8') as file:
                file.write(output)
        else:
            print(output)
    except InvalidLanguageException as err:
        if len(str(err)):
            raise InvalidLanguageException(err)
        elif language not in form.languages:
            msg = 'Specified language not found in form: ' + language
            msg += '\n\nThe form \'{}\' contains the following languages' \
                   '.\n'.format(inpath)
            for lang in form.languages:
                msg += '  * ' + lang + '\n'
            raise InvalidLanguageException(msg[0:-1])
    except OdkChoicesError as err:
        raise OdkFormError(err)
    except OdkFormError as err:
        raise OdkFormError(err)
