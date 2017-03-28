"""Module for the Xlstab class"""
from pmix.worksheet import Worksheet


class Xlstab(Worksheet):

    SURVEY_TRANSLATIONS = (
        'label',
        'hint',
        'constraint_message',
        'audio',
        'video',
        'image'
    )

    CHOICES_TRANSLATIONS = (
        'label',
        'audio',
        'video',
        'image'
    )

    def __init__(self, *, data=None, name=None):
        super().__init__(data=data, name=name)
        self.translate_cols = self.init_translate_cols()

    @classmethod
    def from_worksheet(cls, worksheet):
        xlstab = cls(data=worksheet.data, name=worksheet.name)
        return xlstab

    def init_translate_cols(self):
        pass

    def add_language(self, language):
        if isinstance(language, str):
            language = [language]
        try:
            english, others, translations = self.preprocess_header()
            found_languages = others + [constants.ENGLISH]
            for eng_col, name in english:
                for lang in language:
                    # Do not want to add a language we already have
                    if lang not in found_languages:
                        new_name = constants.BOTH_COL_FORMAT.format(name, lang)
                        self.add_col_name(new_name)
        except TypeError:
            # language not iterable, do nothing
            pass
        except SpreadsheetError:
            # No English found, do nothing
            pass

    # generator returns two dictionaries, each of the same format
    # {
    #   constants.LANGUAGE: "English",
    #   constants.LOCATION: (row, col),
    #   constants.TEXT:     "What is your name?"
    # }
    # First dictionary is for English. Second is for the foreign language
    def translation_pairs(self, ignore=None):
        if ignore is None:
            ignore = []
        try:
            english, others, translations = self.preprocess_header()
            for row, line in enumerate(self):
                if row == 0:
                    continue
                for eng_col, name in english:
                    eng_text = line[eng_col]
                    eng_text = eng_text.strip()
                    eng_dict = {
                        constants.LANGUAGE: constants.ENGLISH,
                        constants.LOCATION: (row, eng_col),
                        constants.TEXT:     eng_text
                    }
                    these_translations = translations[name]
                    for lang in others:
                        if lang in ignore:
                            continue
                        try:
                            lang_col = these_translations[lang]
                            lang_text = line[lang_col]
                            lang_text = lang_text.strip()
                            lang_dict = {
                                constants.LANGUAGE: lang,
                                constants.LOCATION: (row, lang_col),
                                constants.TEXT:     lang_text
                            }
                            # We want to consider it as needing a translation
                            # if there is English text defined.
                            # TODO this may need to change
                            if eng_text != '':
                                yield eng_dict, lang_dict
                        except KeyError:
                            # Translation not found, skip
                            pass
        except SpreadsheetError:
            # Nothing found from preprocess_header
            return
