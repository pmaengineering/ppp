"""Module for the OdkCalculate class."""
from ppp.odkabstractprompt import OdkAbstractPrompt


class OdkCalculate(OdkAbstractPrompt):
    """Class to represent a single ODK calculate from an XLSForm."""

    def __init__(self, row, renderable=False):
        """Initialize OdkCalculate.

        Args:
            row (dict): XLSForm headers as keys, row entries as values. It is
                guaranteed to have the "simple_type" key with a value from the
                class member variables `select_types`,
                `visible_response_types`, or `visible_non_response_types`.
            renderable (bool): Render the calculate?
        """
        super().__init__(row)
        self.renderable = renderable

    def to_html(self, lang, **kwargs):
        """Overriding to_html"""
        if self.renderable:
            return super(OdkCalculate, self).to_html(lang, **kwargs)
        else:
            return ""
