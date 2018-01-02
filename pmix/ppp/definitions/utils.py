"""Utils."""
from ..config import EXCLUSION_TOKEN
from .constants import PRESETS


def exclusion(item, settings):
    """Identify item as to be excluded or not.

    Identify whether item should be excluded from rendering based on whether
    there is presence of exclusion token in the ppp_excludes field of an
    XlsForm, assuming the user has determined that there should be exclusions,
    based on explicit 'exclusion' parameter, or via certain preset options.

    Args:
        item (object): Object of type OdkPrompt, OdkGroup, OdkRepeat, or
            OdkTable.
        settings (dict): Keyword argument settings passed by user to PPP for
            conversion.

    Returns
        bool: True if item should be excluded, else False.
    """
    config = {
        'error_on_no_exclude_column_for_preset': False
    }
    exclude = False

    try:
        if 'exclusion' in settings or 'preset' in settings \
                and PRESETS[settings['preset']]['general_exclusions']:

            if hasattr(item, 'row'):
                item_data = 'row'
            elif hasattr(item, 'opener'):
                item_data = 'opener'
            else:
                # Table; Rather than explicitly exluding a table, the group
                # itself should be excluded.
                return False

            token = EXCLUSION_TOKEN.lower()
            exclude = getattr(item, item_data)['ppp_excludes'].lower() == token

        return exclude
    except KeyError:
        err = True
        if config['error_on_no_exclude_column_for_preset'] == False \
                and 'preset' in settings:
            err = False
        if err:
            msg = 'If using exclusion option or preset with exclusions, ' \
                  'XlsForm must have field named \'ppp_excludes\'.'
            raise KeyError(msg)
        else:
            return exclude
