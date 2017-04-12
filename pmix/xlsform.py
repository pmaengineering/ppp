"""This module defines the Xlsform class to work with ODK XLSForms"""

from pmix.verbiage import TranslationDict
from pmix.xlstab import Xlstab
from pmix.workbook import Workbook


class Xlsform(Workbook):
    """Class to represent an Xlsform spreadsheet.

    The Xlsform class extends the Workbook class to provide functionality
    related specifically to Xlsforms and would not be expected for a general-
    purpose Workbook.

    Note: Analogously, the Xlstab class extends the Worksheet class.
    """

    def __init__(self, path):
        """Initialize workbook and cache Xlsform-specific info.

        Args:
            path (str): The path where to find the Xlsform file.
        """
        super().__init__(path)
        self.data = [Xlstab.from_worksheet(ws) for ws in self]
        self.init_settings()

    def init_settings(self):
        """Get settings from Xlsform.

        Post-condition: the Xlsform's settings are stored in the instance.
        """
        try:
            local_settings = self['settings']
            headers = local_settings[0]
            values = local_settings[1]
            self.settings = {str(k): v for k, v in zip(headers, values) if not
                    k.is_blank()}
        except (KeyError, IndexError):
            self.settings = {}

    @property
    def form_id(self):
        """Return form_id setting value."""
        self.init_settings()
        form_id = self.settings['form_id']
        return str(form_id)

    @property
    def form_title(self):
        """Return form_title setting value."""
        self.init_settings()
        form_title = self.settings['form_title']
        return str(form_title)

    def add_language(self, language):
        """Add appropriate language columns to an Xlsform.

        Args:
            language (str): The language to add to all relevant sheets.
        """
        for sheet in self:
            sheet.add_language(language)

    def merge_translations(self, translations, ignore=None):
        """Merge translations"""
        for sheet in self:
            sheet.merge_translations(translations, ignore)

    def create_translation_dict(self, ignore=None):
        """Create a TranslationDict object from this Xlsform"""
        result = TranslationDict()
        for sheet in self:
            this_result = sheet.create_translation_dict(ignore)
            result.update(this_result)
        return result
