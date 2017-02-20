"""
Class to represent a single ODK prompt from an XLSForm.
"""


import pmix.utils


class Odkprompt:

    select_types = (
        'select_one',
        'select_multiple'
    )

    response_types = (
        'integer',
        'decimal',
        'geopoint',
        'image',
        'text',
        'date',
        'dateTime'
    )

    non_response_types = (
        'note'
    )

    def __init__(self, row, choices=None):
        """

        Row is a dict object. It is guaranteed to have the "simple_type" key
        with a value from the class member variables.

        :param row: Dictionary with languages as keys
        :param choices: An Odkchoices object
        """
        self.row = row
        self.choices = choices

        self.odktype = self.row['simple_type']

    def text_field(self, field, lang=None):
        if lang:
            key = '{}::{}'.format(field, lang)
            value = self.row[key]
        else:
            langs = self.langs(field)
            first = langs[0]
            # TODO: Possible key error
            lang_col = '{}::{}'.format(field, first) if first else field
            value = self.row[lang_col]
        return value

    def langs(self, field):
        langs = []
        for k in self.row:
            if k == field:
                langs.append('')
            elif k.startswith(field + '::'):
                lang = k[len(field + '::'):]
                langs.append(lang)
        return sorted(langs)

    def to_text_response(self, lang=None):
        choices = self.choices.labels(lang=lang)

        s = None
        if self.odktype == 'select_multiple' and choices:
            s = '\n'.join(('_ {}'.format(i) for i in choices))
        elif self.odktype == 'select_one' and self.choices:
            s = '\n'.join(('* {}'.format(i) for i in choices))
        elif self.odktype in Odkprompt.response_types:
            s = '_'*30 + '({})'.format(self.odktype)

        # try:
        #     question_type = self.odktype in Odkprompt.response_types or \
        #                     self.odktype in Odkprompt.select_types
        #     if s and self.row['read_only'] and question_type:
        #         # TODO fix read_only lookup
        #         s = '\n'.join(('[Read only]', s))
        # except KeyError:  # Unable to find 'read_only'
        #     pass
        return s

    def to_text(self, lang=None):
        label = self.text_field('label', lang)
        hint = self.text_field('hint', lang)
        text = filter(None, (label, hint, self.to_text_response(lang)))
        result = '\n\n'.join(text)
        return result
