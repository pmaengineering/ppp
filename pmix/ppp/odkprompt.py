#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OdkPrompt."""
import textwrap
from pmix.ppp.ppp_config import TEMPLATE_ENV


class OdkComponent:
    """Base class for ODK components that comprise an ODK Form."""

    def __init__(self):
        """Initialize."""
        self.media_fields = ['image', 'media::image', 'audio', 'media::audio',
                             'video', 'media::video']
        self.language_dependent_fields = \
            ['label', 'hint', 'constraint_message'] + self.media_fields
        self.truncatable_fields = ['constraint', 'relevant']

    @staticmethod
    def truncate_text(text):
        """Truncate text and add an ellipsis when text is too long.

        :param text: (str) The text.
        :return: (str) Truncated text.
        """
        if len(text) > 100:
            text = text[0:98] + ' …'
        return text

    def truncate_fields(self, row):
        """Call truncate_text() method for all truncatable fields in component.

        :param row: (str) The dictionary row of the component.
        :return: (d) Dictionary row of the component, reformatted.
        """
        for field in self.truncatable_fields:
            row[field + '_original'] = row[field]
            row[field] = self.truncate_text(row[field])
        return row

    def reformat_default_lang_vars(self, row, lang):
        """Reformat default language variables.

        Reformat ::<language_name> style variable names to remove the
        ::<language_name>, leaving just the variable.

        :param row: (str) The dictionary row of the component.
        :param lang: (str) The language.
        :return: (str) Dictionary row of the component, reformatted.
        """
        for field in self.language_dependent_fields:
            if field + '::' + lang in row:
                row[field] = row[field + '::' + lang]
        return row

    # pylint: disable=too-many-branches
    def create_additional_media_fields(self, row, prefix):
        """Create additional media fields."""
        fields_to_add = []
        for key, val in row.items():
            for field in self.media_fields:
                if key.startswith(field) and len(val) > 0:
                    if field not in row:
                        fields_to_add.append(field)
                    if field.startswith(prefix):
                        non_prefixed_mf = field.replace(
                            prefix, '')
                        if non_prefixed_mf not in row:
                            fields_to_add.append(non_prefixed_mf)

        for field in fields_to_add:
            row[field] = ''
        if len(fields_to_add) > 0:
            row['media'] = ''
        return row

    def format_media_labels(self, input_row):
        """Format media labels."""
        arbitrary_media_prefix = 'media::'
        row = self.create_additional_media_fields(input_row,
                                                  arbitrary_media_prefix)
        for key, val in row.items():
            for field in self.media_fields:
                if key.startswith(field) and len(val) > 0:
                    if val[0] is not '[' and val[-1] is not ']':
                        formatted_media_label = '[' + val + ']'
                    row[field] = formatted_media_label
                    row[key] = formatted_media_label
                    if field.startswith(arbitrary_media_prefix):
                        non_prefixed_mf = field.replace(
                            arbitrary_media_prefix, '')
                        row[non_prefixed_mf] = formatted_media_label
        return row

    def set_grouped_media_field(self, row, lang):
        """Format the text representing any media to be enclosed in brackets.

        :param row: (str) The dictionary row of the component.
        :param lang: (str) The language.
        :return: (str) Dictionary row of the component, reformatted.
        """
        for key, val in row.items():
            for field in self.media_fields:
                if key.startswith(field + '::' + lang) and len(val) > 0:
                    if len(row['media']) > 1:
                        row['media'] += '\n'
                    row['media'] += val
        return row


class OdkPrompt(OdkComponent):
    """
    Class to represent a single ODK prompt from an XLSForm.

    This is described in a single row of an XLSForm.
    """

    select_types = (
        'select_one',
        'select_multiple'
    )

    response_types = (
        'integer',
        'decimal',
        'geopoint',
        'barcode',
        'image',
        'text',
        'date',
        'dateTime'
    )

    non_response_types = (
        'note',
    )

    def __init__(self, row, choices=None):
        """Initialize the XLSForm prompt (a single row of a specific type).

        Row is a dict object. It is guaranteed to have the "simple_type" key
        with a value from the class member variables `select_types`,
        `response_types`, or `non_response_types`.

        :param row: (dict) XLSForm headers as keys, row entries as values.
        :param choices: An Odkchoices object, or None if not a select type.
        """
        OdkComponent.__init__(self)
        self.row = row
        self.choices = choices
        self.odktype = self.row['simple_type']
        self.is_section_header = True if self.row['name'].startswith('sect_') \
            else False

    def __repr__(self):
        """Print representation of instance."""
        return "<OdkPrompt {}>".format(self.row['name'])

    @staticmethod
    def text_relevant():
        # def text_relevant(self, lang):
        # TODO: Create this method.
        """Find the relevant text for this row."""
        pass

    def text_field(self, field, lang):
        """Find a row value given a field and language.

        An example of field and language might be "label" and "English".

        :param field: (str) The field from the header row.
        :param lang: (str) The language.
        :return: (str) The value found from this row.
        """
        value = None
        try:
            if lang:
                key = '{}::{}'.format(field, lang)
                value = self.row[key]
            else:
                keys = (k for k in self.row if k.startswith(field))
                first = sorted(keys)[0]
                value = self.row[first]
        except (KeyError, IndexError):
            # KeyError: self.row does not have the key '{}::{}'
            # IndexError: `keys` (filtered by field) is empty list
            pass
        return value

    def to_text_relevant(self, lang):
        """Get the relevant text for this prompt.

        :param lang: (str) The language.
        :return: (str) The text representation of the relevant.
        """
        formatted_relevant = None
        relevant_text = self.text_field('relevant_text', lang)
        if relevant_text:
            formatted_relevant = '[{}]'.format(relevant_text).rjust(50)
        return formatted_relevant

    def to_text_response(self, lang, numbered=False):
        """Get the response field for this prompt.

        This is a text representation of the area of a paper questionnaire
        where the response is recorded.

        :param lang: (str) The language.
        :param numbered: (bool) Should choice options be numbered?
        :return: (str) The text representation of the response entry field.
        """
        text_str = None
        if self.odktype == 'select_multiple':
            choices = self.choices.labels(lang=lang)
            if numbered:
                choices = ['{}. {}'.format(i+1, c) for i, c in
                           enumerate(choices)]
            text_str = '\n'.join(('_ {}'.format(i) for i in choices))
        elif self.odktype == 'select_one':
            choices = self.choices.labels(lang=lang)
            if numbered:
                choices = ['{}. {}'.format(i+1, c) for i, c in
                           enumerate(choices)]
            text_str = '\n'.join(('* {}'.format(i) for i in choices))
        elif self.odktype in OdkPrompt.response_types:
            text_str = '_'*30 + '({})'.format(self.odktype)

        # try:
        #     question_type = self.odktype in Odkprompt.response_types or \
        #                     self.odktype in Odkprompt.select_types
        #     if text_str and self.row['read_only'] and question_type:
        #         # TODO fix read_only lookup
        #         text_str = '\n'.join(('[Read only]', text_str))
        # except KeyError:  # Unable to find 'read_only'
        #     pass

        if text_str:
            text_str = textwrap.indent(text_str, '  ')

        return text_str

    def to_html_input_field(self, lang):
        """Get the response field for this prompt.

        This is a representation of the area of a paper questionnaire where
        the response is recorded.

        :param lang: (str) The language.
        :return: (str or dict) The representation of the entry field.
        """
        field = None
        if self.odktype in ['select_multiple', 'select_one']:
            field = self.choices.name_labels(lang=lang)
        elif self.odktype in OdkPrompt.response_types:
            field = '_' * 30 + '({})'.format(self.odktype)
        return field

    def to_text(self, lang):
        """Get the text representation of the full prompt.

        :param lang: (str) The language.
        :return: (str) The text from all parts of the prompt.
        """
        # Note: May not need 'relevant_text'.
        # relevant_text = self.text_field('relevant_text', lang)
        label = self.text_field('label', lang)
        hint = self.text_field('hint', lang)
        # Need done: Audio, Image, Video, Relevant
        fields = (
            self.to_text_relevant(lang),
            label,
            hint,
            self.to_text_response(lang)
        )
        text = filter(None, fields)
        result = '\n\n'.join(text)
        return result

    def to_dict(self, lang, **kwargs):
        """Get the text representation of the full prompt.

        :param lang: (str) The language.
        :return: (dict) The text from all parts of the prompt.
        """
        # TODO: Refactor so that the dict row is only looped through once
        # to make all of the changes below.
        prompt = self.format_media_labels(self.row)
        prompt = self.set_grouped_media_field(prompt, lang)
        prompt = self.reformat_default_lang_vars(prompt, lang)
        prompt = self.truncate_fields(prompt)
        prompt['input_field'] = self.to_html_input_field(lang)
        if self.is_section_header:
            prompt['is_section_header'] = True
        if 'bottom_border' in kwargs:
            prompt['bottom_border'] = True
        return prompt

    def to_html(self, lang, highlighting, **kwargs):
        """Convert to html."""
        # pylint: disable=no-member
        return TEMPLATE_ENV.get_template('content/content-tr-base.html')\
            .render(question=self.to_dict(lang=lang, **kwargs),
                    highlighting=highlighting)
