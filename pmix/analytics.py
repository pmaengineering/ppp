#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Get the tracked fields for PMA Analytics.

Need to be able to get the ODK names from files (possibly collapse across
groups)

"""

import argparse
import datetime
import json

from pmix.xlsform import Xlsform


def is_analytics_type(odk_type):
    """Test if an odk type is suitable for tracking in analytics.

    Args:
        odk_type (str): The type to test

    Returns:
        Return true if and only if odk_type is good for analytics
    """
    bad_types = (
        'type',
        'calculate',
        'hidden',
        'start',
        'end',
        'begin ',
        'deviceid',
        'simserial',
        'phonenumber'
    )
    bad = any((odk_type.startswith(bad) for bad in bad_types))
    return not bad and odk_type != ''


def get_filtered_survey_names(xlsform):
    """Return the ODK names from 'survey' to track in analytics.

    Args:
        xlsform (pmix.Xlsform): An xlsform (workbook) object

    Returns:
        A list of ODK names to use in analytics.
    """
    odk_type = xlsform['survey'].column('type')
    odk_name = xlsform['survey'].column('name')
    filtered = [str(n) for t, n in zip(odk_type, odk_name) if
                is_analytics_type(str(t))]
    return filtered


def get_useful_tags(xlsform):
    """Return the ODK tags from 'survey' to retrieve the value for.

    This function compares each ODK 'name' to a pre-approved list and keeps
    that name if there is a match.

    Args:
        xlsform (pmix.Xlsform): An xlsform (workbook) object

    Returns:
        A list of ODK tags to track in analytics.
    """
    useful_tags = (
        'your_name',
        'name_typed',
        'level1',
        'level2',
        'level3',
        'level4',
        'EA',
        'structure',
        'household',
        'level1_unlinked',
        'level2_unlinked',
        'level3_unlinked',
        'level4_unlinked',
        'EA_unlinked',
        'facility_type',
        'deviceid',
        'start',
        'end',
        'HHQ_result',
        'FRS_result',
        'SDP_result'
    )
    odk_name = set(str(c) for c in xlsform['survey'].column('name'))
    keepers = [t for t in useful_tags if t in odk_name]
    return keepers


def analytics_obj(xlsxfile):
    """Create an analytics object based on supplied path."""
    xls = Xlsform(xlsxfile)
    form_id = xls.form_id
    form_title = xls.form_title
    prompts = get_filtered_survey_names(xls)
    tags = get_useful_tags(xls)
    today = str(datetime.date.today())
    obj = {
        'form_id': form_id,
        'form_title': form_title,
        'prompts': prompts,
        'tags': tags,
        'created': today,
        '~comment': 'END {}'.format(form_id)
    }
    return obj


def get_analytics_objs(xlsxfiles):
    """Get the list of analytics objects based on supplied paths."""
    return [analytics_obj(xlsxfile) for xlsxfile in set(xlsxfiles)]


def prettify(obj):
    """Get the prettified string to represent the supplied object."""
    return json.dumps(obj, sort_keys=True, indent=2)


def analytics_cli():
    """Run the command line interface for this module."""
    prog_desc = 'Help facilitate analytics by extracting useful information.'
    parser = argparse.ArgumentParser(description=prog_desc)

    file_help = 'One or more paths to source XLSForms.'
    parser.add_argument('xlsxfile', nargs='+', help=file_help)

    out_help = ('Path to write output. If this argument is not supplied, then '
                'result is sent to standard out.')
    parser.add_argument('-o', '--outpath', help=out_help)

    args = parser.parse_args()

    objs = get_analytics_objs(args.xlsxfile)
    result = prettify(objs)
    if args.outpath:
        with open(args.outpath, mode='w', encoding='utf-8') as out:
            out.write(result)
        print('Wrote analytics file to "{}"'.format(args.outpath))
    else:
        print(result)


if __name__ == '__main__':
    analytics_cli()
