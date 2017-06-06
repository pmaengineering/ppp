#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A package for converting ODK forms."""
from pmix.ppp.odkform import OdkForm
from pmix.ppp.error import OdkFormError, InvalidLanguageException


def run(inpath, language, output_format, outfile, **kwargs):
    """Run ODK form conversion.

    Args:
        inpath (str): Path to load source file.
        language (str): Language to render form.
        output_format (str): File format to be output.
        outfile (str): Path to save converted file.
        **debug (bool): Debugging on or off.
        **highlight (bool): Highlighting on or off.
    """
    survey = None
    form = OdkForm(file=inpath)
    try:
        if output_format == 'text':
            survey = form.to_text(language)
        elif output_format == 'dict':
            survey = form.to_dict(language)
        elif output_format == 'json':
            # pylint: disable=redefined-variable-type
            survey = form.to_json(language, pretty=False)
        elif output_format == 'json_pretty':
            survey = form.to_json(language, pretty=True)
        elif output_format == 'html' or not output_format:
            survey = form.to_html(language, kwargs['highlight'],
                                  kwargs['debug'])
        if outfile:
            with open(outfile, mode='w', encoding='utf-8') as file:
                file.write(survey)
        else:
            print(survey)
    except InvalidLanguageException as e:
        raise InvalidLanguageException(e)
    except OdkFormError as e:
        raise OdkFormError(e)
    except:
        if language not in form.languages:
            msg = '\nSpecified language not found in form: ' + language
            msg += '\n\nThe form \'{}\' contains the following languages' \
                   '.\n'.format(inpath)
            for lang in form.languages:
                msg += '  * ' + lang + '\n'
            raise InvalidLanguageException(msg[0:-1])
        else:
            raise BaseException
