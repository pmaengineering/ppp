from jinja2 import Environment, PackageLoader
import textwrap


class OdkComponent:
    def __init__(self):
        self.language_dependent_fields = ['label', 'hint', 'constraint_message', 'image', 'audio', 'video']
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

class Odkprompt(OdkComponent):
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

    def __repr__(self):
        s = "<Odkprompt {}>".format(self.row['name'])
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
        if self.odktype == 'select_multiple':
            choices = self.choices.labels(lang=lang)
            field = choices
        elif self.odktype == 'select_one':
            choices = self.choices.labels(lang=lang)
            field = choices
        elif self.odktype in Odkprompt.response_types:
            field = '_'*30 + '({})'.format(self.odktype)

        return field

    # @staticmethod
    # def truncate_text(text):
    #     """Truncate text and add an ellipsis when text is too long.
    #
    #     :param text: (str) The text.
    #     :return: (str) Truncated text.
    #     """
    #     if len(text) > 100:
    #         text = text[0:98] + ' …'
    #     return text

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
    #
    # def reformat_default_language_variable_names(self, d, lang):
    #     language_dependent_field = ['label', 'hint', 'constraint_message', 'image', 'audio', 'video']
    #     for field in language_dependent_field:
    #         if (field + '::' + lang) in d:
    #             d[field] = d[field + '::' + lang]
    #     truncatable_fields = ['constraint', 'relevant']
    #     for field in truncatable_fields:
    #         d[field + '_original'] = d[field]
    #         d[field] = self.truncate_text(d[field])
    #     d['input_field'] = self.to_html_input_field(lang)
    #     return d

    def to_dict(self, lang):
        """Get the text representation of the full prompt

        :param lang: (str) The language.
        :return: (dict) The text from all parts of the prompt.
        """
        d = self.reformat_default_language_variable_names(self.row, lang)
        d = self.truncate_fields(d)
        d['input_field'] = self.to_html_input_field(lang)
        return d

    def to_html(self, lang, highlighting):
        env = Environment(loader=PackageLoader('pmix'))
        question = env.get_template('content/content-tr-base.html').render(question=self.to_dict(lang=lang),
                                                                           highlighting=highlighting)
        return question
