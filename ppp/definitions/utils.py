"""Utils."""
from ppp.definitions.constants import EXCLUSION_TOKEN, TEMPLATES


def exclusion(item, settings):
    """Identify item as to be excluded or not.

    Identify whether item should be excluded from rendering based on whether
    there is presence of exclusion token in the ppp_excludes field of an
    XlsForm, assuming the user has determined that there should be exclusions,
    based on explicit 'exclusion' parameter, or via certain preset template
    options.

    Args:
        item (object): Object of type OdkPrompt, OdkGroup, OdkRepeat, or
            OdkTable.
        settings (dict): Keyword argument settings passed by user to PPP for
            conversion.

    Returns
        bool: True if item should be excluded, else False.
    """
    config = {"error_on_no_exclude_column": False}
    exclude = False

    try:
        if (
            "exclusion" in settings
            or "template" in settings
            and TEMPLATES[settings["template"]]["general_exclusions"]
        ):

            if hasattr(item, "row"):
                item_data = "row"
            elif hasattr(item, "row"):
                item_data = "row"
            else:
                # Table; Rather than explicitly exluding a table, the group
                # itself should be excluded.
                return False

            token = EXCLUSION_TOKEN.lower()
            try:
                exclude = getattr(item, item_data)["ppp_excludes"].lower() == token
            except TypeError:
                pass

        return exclude
    except KeyError:
        err = True
        if not config["error_on_no_exclude_column"] and "template" in settings:
            err = False
        if err:
            msg = (
                "If using exclusion option or template that uses "
                "exclusions, XlsForm must have field named 'ppp_excludes'."
            )
            raise KeyError(msg)
        else:
            return exclude
