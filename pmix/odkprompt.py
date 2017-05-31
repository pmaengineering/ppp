import textwrap
from jinja2 import Environment, PackageLoader


class OdkComponent:
    def __init__(self):
        self.media_fields = ['image', 'media::image', 'audio', 'media::audio', 'video', 'media::video']
        self.non_duplicated_media_fields = self.set_non_duplicated_media_fields(self.media_fields)
        self.language_dependent_fields = ['label', 'hint', 'constraint_message'] + self.media_fields
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

    def truncate_fields(self, d):
        """Call truncate_text() method for all truncatable fields in component.

        :param d: (str) The dictionary row of the component.
        :return: (d) Dictionary row of the component, reformatted.
        """
        for field in self.truncatable_fields:
            d[field + '_original'] = d[field]
            d[field] = self.truncate_text(d[field])
        return d

    def reformat_default_language_variable_names(self, d, lang):
        """Reformat ::<language_name> style variable names to remove the ::<language_name>, leaving just the variable.

        :param d: (str) The dictionary row of the component.
        :param lang: (str) The language.
        :return: (str) Dictionary row of the component, reformatted.
        """
        for field in self.language_dependent_fields:
            if (field + '::' + lang) in d:
                d[field] = d[field + '::' + lang]
        return d

    def set_non_duplicated_media_fields(self, media_fields):
        non_duplicated_media_fields = []
        for field in media_fields:
            if '::' not in media_fields:
                non_duplicated_media_fields.append(field)
        return non_duplicated_media_fields

    def format_media_labels(self, d):
        arbitrary_media_prefix = 'media::'

        fields_to_add = []
        for key, val in d.items():
            for mf in self.media_fields:
                if key.startswith(mf) and len(val) > 0:
                    if mf not in d:
                        fields_to_add.append(mf)
                    if mf.startswith(arbitrary_media_prefix):
                        non_prefixed_mf = mf.replace(arbitrary_media_prefix, '')
                        if non_prefixed_mf not in d:
                            fields_to_add.append(non_prefixed_mf)

        for field in fields_to_add:
            d[field] = ''
        if len(fields_to_add) > 0:
            d['media'] = ''

        for key, val in d.items():
            for mf in self.media_fields:
                if key.startswith(mf) and len(val) > 0:
                    if val[0] is not '[' and val[-1] is not ']':
                        formatted_media_label = '[' + val + ']'
                    d[mf] = formatted_media_label
                    d[key] = formatted_media_label
                    if mf.startswith(arbitrary_media_prefix):
                        non_prefixed_mf = mf.replace(arbitrary_media_prefix, '')
                        d[non_prefixed_mf] = formatted_media_label
        return d

    def set_grouped_media_field(self, d, lang):
        """Format the text representing any media to be enclosed in brackets.

        :param d: (str) The dictionary row of the component.
        :return: (str) Dictionary row of the component, reformatted.
        """
        for key, val in d.items():
            for field in self.media_fields:
                if key.startswith(field + '::' + lang) and len(val) > 0:
                    if len(d['media']) == 0:
                        d['media'] += '['
                    if len(d['media']) > 1:
                        d['media'] += ' / '
                    d['media'] += 'Image: ' if key.startswith('image' or 'media::image') \
                        else 'Audio: ' if key.endswith('audio' or 'media::audio') \
                        else 'Video: ' if key.endswith('video' or 'media::video') else ''
                    d['media'] += val
                    d['media'] += ']'
        return d


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
        """Initialize the XLSForm prompt (a single row of a specific type)

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
        self.is_section_header = True if self.row['name'].startswith('sect_') else False

    def __repr__(self):
        s = "<OdkPrompt {}>".format(self.row['name'])
        return s

    @staticmethod
    def text_relevant(self, lang):
        # TODO: Create this method.
        """Find the relevant text for this row"""
        pass

    def text_field(self, field, lang):
        """Find a row value given a field and language

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
        """Get the relevant text for this prompt

        :param lang: (str) The language
        :return: (str) The text representation of the relevant
        """
        s = None
        relevant_text = self.text_field('relevant_text', lang)
        if relevant_text:
            s = '[{}]'.format(relevant_text).rjust(50)
        return s

    def to_text_response(self, lang, numbered=False):
        """Get the response field for this prompt

        This is a text representation of the area of a paper questionnaire
        where the response is recorded.

        :param lang: (str) The language
        :param numbered: (bool) Should choice options be numbered?
        :return: (str) The text representation of the response entry field
        """
        s = None
        if self.odktype == 'select_multiple':
            choices = self.choices.labels(lang=lang)
            if numbered:
                choices = ['{}. {}'.format(i+1, c) for i, c in
                           enumerate(choices)]
            s = '\n'.join(('_ {}'.format(i) for i in choices))
        elif self.odktype == 'select_one':
            choices = self.choices.labels(lang=lang)
            if numbered:
                choices = ['{}. {}'.format(i+1, c) for i, c in
                           enumerate(choices)]
            s = '\n'.join(('* {}'.format(i) for i in choices))
        elif self.odktype in OdkPrompt.response_types:
            s = '_'*30 + '({})'.format(self.odktype)

        # try:
        #     question_type = self.odktype in Odkprompt.response_types or \
        #                     self.odktype in Odkprompt.select_types
        #     if s and self.row['read_only'] and question_type:
        #         # TODO fix read_only lookup
        #         s = '\n'.join(('[Read only]', s))
        # except KeyError:  # Unable to find 'read_only'
        #     pass

        if s:
            s = textwrap.indent(s, '  ')

        return s

    def to_html_input_field(self, lang):
        """Get the response field for this prompt

        This is a representation of the area of a paper questionnaire where the response is recorded.

        :param lang: (str) The language.
        :return: (str or dict) The representation of the entry field
        """
        field = None
        if self.odktype in ['select_multiple', 'select_one']:
            field = self.choices.name_labels(lang=lang)
        elif self.odktype in OdkPrompt.response_types:
            field = '_' * 30 + '({})'.format(self.odktype)
        return field

    def to_text(self, lang):
        """Get the text representation of the full prompt

        :param lang: (str) The language
        :return: (str) The text from all parts of the prompt
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
        """Get the text representation of the full prompt

        :param lang: (str) The language.
        :return: (dict) The text from all parts of the prompt.
        """
        # TODO: Refactor so that the dict row is only looped through once to make all of the changes below.
        d = self.format_media_labels(self.row)
        d = self.set_grouped_media_field(d, lang)
        d = self.reformat_default_language_variable_names(d, lang)
        d = self.truncate_fields(d)
        d['input_field'] = self.to_html_input_field(lang)
        if self.is_section_header:
            d['is_section_header'] = True
        if 'bottom_border' in kwargs:
            d['bottom_border'] = True
        return d

    def to_html(self, lang, highlighting, **kwargs):
        env = Environment(loader=PackageLoader('pmix'))
        question = env.get_template('content/content-tr-base.html').render(question=self.to_dict(lang=lang, **kwargs),
                                                                           highlighting=highlighting)
        return question
