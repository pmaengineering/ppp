from pmix.workbook import Workbook


class Xlsform(Workbook):
    """Class to represent an Xlsform spreadsheet"""

    def __init__(self, file):
        super().__init__(file)
        self.initialize_settings()
        
    def initialize_settings(self):
        try:
            local_settings = self['settings']
            headers = local_settings[0]
            values = local_settings[1]
            self.settings = {k: v for k, v in zip(headers, values) if k}
        except (KeyError, IndexError):
            self.settings = {}

    def get_form_id(self):
        """Get the form id for the Xlsform"""
        settings = self[constants.SETTINGS]
        col = settings.column(constants.FORM_ID)
        heading = next(col) # discard
        form_id = next(col)
        return form_id

    def add_language(self, language):
        """Add appropriate language columns to an Xlsform"""
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
