"""Utils."""
from ..odkprompt import OdkPrompt
from ..odkgroup import OdkGroup
from ..odkrepeat import OdkRepeat
from ..odktable import OdkTable
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
    exclude = False

    if 'exclusion' in settings or 'preset' in settings \
            and PRESETS[settings['preset']['exlcusion']]:

        item_data = ''
        if isinstance(item, OdkPrompt):
            item_data = 'row'
        elif isinstance(item, OdkGroup or OdkRepeat):
            item_data = 'opener'
        elif isinstance(item, OdkTable):
            return False  # TODO
        exclude = \
            getattr(item, item_data)['ppp_excludes'].lower() == \
            EXCLUSION_TOKEN.lower()

    return exclude
