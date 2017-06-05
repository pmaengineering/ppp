#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A package for converting ODK XlsForms into HTML."""
from pmix.ppp.odkform import OdkForm


def run(inpath, language, output_format, outfile, **kwargs):
    """Runs ODK form conversion."""

    survey = None
    form = OdkForm(file=inpath)
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
        with open(outfile, mode='w', encoding='utf-8') as f:
            f.write(survey)
    else:
        print(survey)
