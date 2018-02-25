"""Module defining Xlsform class to work with ODK XLSForms."""
from pmix.xlstab import Xlstab
from pmix.workbook import Workbook


class Xlsform(Workbook):
    """Class to represent an Xlsform spreadsheet.

    The Xlsform class extends the Workbook class to provide functionality
    related specifically to Xlsforms and would not be expected for a general-
    purpose Workbook.

    Note: Analogously, the Xlstab class extends the Worksheet class.
    """

    def __init__(self, path, stripstr=True):
        """Initialize workbook and cache Xlsform-specific info.

        Args:
            path (str): The path where to find the Xlsform file.
            stripstr (bool): Remove trailing / leading whitespace from text?
        """
        super().__init__(path, stripstr)
        self.data = [Xlstab.from_worksheet(ws) for ws in self]
        self.settings = {}
        self.init_settings()

    def init_settings(self):
        """Get settings from Xlsform.

        Post-condition: the Xlsform's settings are stored in the instance.
        """
        try:
            local_settings = self['settings']
            headers = local_settings[0]
            values = local_settings[1]
            self.settings = {str(k): str(v) for k, v in zip(headers, values) if
                             not k.is_blank() and not v.is_blank()}
        except (KeyError, IndexError):
            self.settings = {}

    @property
    def form_id(self):
        """Return form_id setting value."""
        self.init_settings()
        form_id = self.settings['form_id']
        return form_id

    @property
    def form_title(self):
        """Return form_title setting value."""
        self.init_settings()
        form_title = self.settings['form_title']
        return form_title

    @property
    def settings_language(self):
        """Return default language from settings or None if not found."""
        self.init_settings()
        default_language = self.settings.get('default_language', None)
        return default_language

    @property
    def survey_languages(self):
        """Retur sorted languages from headers for survey worksheet."""
        return self['survey'].sheet_languages()

    @property
    def form_language(self):
        """Return default language for a form.

        Considers settings tab first, then gets language from survey tab.

        Returns:
            A string for the default language or None if there is no language
            specified.
        """
        language = self.settings_language
        if language is None:
            try:
                language = self.survey_languages[0]
            except KeyError:
                # Keep language as None
                pass
        return language

    def add_language(self, language):
        """Add appropriate language columns to an Xlsform.

        Args:
            language (str): The language to add to all relevant sheets.
        """
        for sheet in self:
            sheet.add_language(language)

    def merge_translations(self, translations, ignore=None, carry=False,
                           no_diverse=False):
        """Merge translations.

        Args:
            translations (TranslationDict): Translations
            ignore (set of str): The languages to ignore when translating
            carry (bool): Carry the source language over to missing translations
            no_diverse (bool): If true, then do not translate text that has
                multiple translations.
        """
        for sheet in self:
            sheet.merge_translations(translations, ignore, carry=carry,
                                     no_diverse=no_diverse)
