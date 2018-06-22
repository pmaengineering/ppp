"""Module for the OdkPrompt class."""
import textwrap

from ppp.config import TEMPLATE_ENV
from ppp.definitions.constants import MEDIA_FIELDS, TRUNCATABLE_FIELDS, \
    LANGUAGE_DEPENDENT_FIELDS, PRESETS, IGNORE_RELEVANT_TOKEN, \
    RELEVANCE_FIELD_TOKENS, PPP_REPLACEMENTS_FIELDS
from ppp.definitions.error import OdkChoicesError


class OdkPrompt:
    """Class to represent a single ODK prompt from an XLSForm.

    This is described in a single row of an XLSForm.

    Attributes:
        row (dict): A dictionary representation of prompt.
        choices (OdkChoices): Answer choices, if applicable.
        odktype (str): The value corresponding to the prompts ODK type.
        is_section_header (bool): Designates whether or not the prompt is a
            section header.

    Class Attributes:
        select_types (tuple): Prompt types which can accept data and include a
            list of choices.
        response_types (tuple): Prompt types which can accept data and do not
            include a list of choices.
        non_response_types (tuple): Prompt types which do not accept data.

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

        Args:
            row (dict): XLSForm headers as keys, row entries as values. It is
                guaranteed to have the "simple_type" key with a value from the
                class member variables `select_types`, `response_types`, or
                `non_response_types`.
            choices (OdkChoices): Answer choices, if applicable.
        """
        self.row = row
        self.choices = choices
        self.odktype = self.row['simple_type']
        self.is_section_header = True if self.row['name'].startswith('sect_') \
            else False
        if self.odktype in OdkPrompt.select_types and self.choices is None:
            msg = 'No choices found for prompt \'{}\' of type \'{}\'.'\
                .format(self.row['name'], self.odktype)
            raise OdkChoicesError(msg)

    def __repr__(self):
        """Print representation of instance."""
        return "<OdkPrompt {}>".format(self.row['name'])

    @staticmethod
    def truncate_text(text):
        """Truncate text and add an ellipsis when text is too long.

        Args:
            text (str): The text.

        Returns:
            str: Truncated text.
        """
        if len(text) > 100:
            text = text[0:98] + ' …'
        return text

    @staticmethod
    def reformat_double_line_breaks(row):
        """Convert labels and hints from strings to lists.

        This conversion process allows for line breaks to be rendered properly
        in html.

        Args:
            row (dict): The dictionary representation of prompt.

        Returns:
            dict: Reformatted representation.
        """
        for k, v in row.items():
            if k.startswith('label') or k.startswith('hint') \
                    or k.startswith('constraint_message'):
                if v:
                    row[k] = v.split('\n\n')
        return row

    @staticmethod
    def reformat_default_lang_vars(row, lang):
        """Reformat default language variables.

        Reformat '::/:<language_name>' style variable names to remove the
        '::/:<language_name>', leaving just the variable.

        Args:
            row (dict): The dictionary representation of prompt.
            lang (str): The language.

        Returns:
            dict: Reformatted representation.
        """
        new_row = row.copy()
        for field in LANGUAGE_DEPENDENT_FIELDS:
            if field + '::' + lang in new_row:
                new_row[field] = new_row[field + '::' + lang]
            elif field + ':' + lang in new_row:
                new_row[field] = new_row[field + ':' + lang]
        return new_row

    # pylint: disable=too-many-branches
    @staticmethod
    def create_additional_media_fields(row, prefix):
        """Create additional media fields.

        Create 'media' field for populating list of all media for prompt.
        Create individual, language-agnostic named media fields for each type
        of media present in prompt, populated with value from corresponding
        media field of default language.

        Args:
            row (dict): The dictionary representation of prompt.
            prefix (str): Prefix for media fields allowed by ODK; 'media::/:'.

        Returns:
            dict: Reformatted representation.
        """
        fields_to_add = []
        new_row = row.copy()
        for key, _ in new_row.items():
            for field in MEDIA_FIELDS:
                if key.startswith(field):
                    if field not in row:
                        fields_to_add.append(field)
                    if field.startswith(prefix):
                        non_prefixed_mf = field.replace(prefix, '')
                        if non_prefixed_mf not in row:
                            fields_to_add.append(non_prefixed_mf)

        for field in fields_to_add:
            row[field] = ''
        if fields_to_add:
            row['media'] = []
        return row

    @staticmethod
    def set_grouped_media_field(row):
        """Populate media field with all media for prompt.

        Args:
            row (dict): The dictionary representation of prompt.

        Returns:
            dict: Reformatted representation of prompt.
        """
        new_row = row.copy()
        for key, val in new_row.items():
            for field in MEDIA_FIELDS:
                if val and key.startswith(field) \
                        and val not in new_row['media']:
                    new_row['media'].append(val)
        return new_row

    @staticmethod
    def text_relevant():  # TODO: Create this method.
        # def text_relevant(self, lang):
        """Find the relevant text for this row."""
        pass

    def truncate_fields(self, row):
        """Call truncate_text() method for all truncatable fields in component.

        Args:
            row (dict): The dictionary representation of prompt.

        Returns:
            dict: Reformatted representation of prompt.
        """
        new_row = row.copy()
        for field in TRUNCATABLE_FIELDS:
            if field in new_row:
                new_row[field + '_original'] = new_row[field]
                new_row[field] = self.truncate_text(new_row[field])
        return new_row

    def format_media_labels(self, row):
        """Format text for all media labels to be enclosed in brackets.

        Args:
            row (dict): Dictionary representation of prompt.

        Returns:
            dict: Reformatted representation.
        """
        arbitrary_media_prefixes = ['media::', 'media:']
        for arb in arbitrary_media_prefixes:
            new_row = \
                self.create_additional_media_fields(row, arb)
            for key, val in new_row.items():
                for field in MEDIA_FIELDS:
                    if key.startswith(field) and val:
                        formatted_media_label = val
                        if val[0] != '[' and val[-1] != ']':
                            formatted_media_label = '[' + val + ']'
                        row[field] = formatted_media_label
                        row[key] = formatted_media_label
                        if field.startswith(arb):
                            non_prefixed_mf = field.replace(
                                arb, '')
                            row[non_prefixed_mf] = formatted_media_label
        return row

    @staticmethod
    def _ignore_relevant(prompt):
        """If applicable, ignores relevant, setting it to an empty string.

         In cases where a preset is used which makes use of human-readable
         relevants via the ppp_relevant::<language> field of an XlsForm, this
         function looks for any IGNORE_RELEVANT_TOKEN present in the field and,
         if present, sets it to an empty string.

        Args:
            prompt (dict): Dictionary representation of prompt.

        Returns
            dict: Reformatted representation.
        """
        for x in RELEVANCE_FIELD_TOKENS:
            if x in prompt:
                if prompt[x] == IGNORE_RELEVANT_TOKEN:
                    prompt[x] = ''
        return prompt

    @staticmethod
    def set_descriptive_metadata(prompt):
        """Set descriptive metadata.

        Args:
            prompt (dict): Dictionary representation of prompt.

        Returns
            dict: Reformatted representation.
        """
        prompt['is_section'] = False
        if prompt['simple_type'] == 'note' \
                and prompt['name'].startswith('sect_'):
            prompt['is_section'] = True
        return prompt

    @staticmethod
    def handle_preset(prompt, lang, preset):
        """Handle preset.

        Args:
            prompt (dict): Dictionary representation of prompt.
            lang (str): The language.
            preset (str): The preset supplied.

        Returns
            dict: Reformatted representation.
        """
        # TODO: (jef 2017.09.24) Human readable: hint variables.
        # TODO: (jef 2017.09.24) Human readable: choice filters, calcs.
        for key in prompt:
            for exclusion in PRESETS[preset]['field_exclusions']:
                if key.startswith(exclusion):
                    prompt[key] = ''
                    continue

            for to_replace in PRESETS[preset]['field_replacements']:
                replace_withs = ['ppp_'+to_replace+'::'+lang,
                                 'ppp_'+to_replace+':'+lang]
                for replace_with in replace_withs:
                    if key == replace_with and prompt[replace_with]:
                        for x in PPP_REPLACEMENTS_FIELDS:
                            if to_replace.startswith(x):
                                prompt[to_replace] = [prompt[replace_with]]

            if 'choice names' in PRESETS[preset]['other_specific_exclusions']:
                if key == 'input_field' and prompt['simple_type'] in \
                        ('select_one', 'select_multiple'):
                    prompt['input_field'] = [
                        {'name': '', 'value': '', 'label': i['label']}
                        for i in prompt['input_field']
                    ]

        OdkPrompt._ignore_relevant(prompt)

        return prompt

    def text_field(self, field, lang):
        """Find a row value given a field and language.

        An example of field and language might be "label" and "English".

        Args:
            field (str): The field from the header row.
            lang (str): The language.

        Returns:
            str: The value found from this row.
        """
        value = None
        try:
            if lang:
                if '{}::{}'.format(field, lang) in self.row:
                    key = '{}::{}'.format(field, lang)
                else:
                    key = '{}:{}'.format(field, lang)
                value = self.row[key]
            else:
                keys = (k for k in self.row if k.startswith(field))
                first = sorted(keys)[0]
                value = self.row[first]
        except (KeyError, IndexError):
            # KeyError: self.row does not have the key '{}::/:{}'.
            # IndexError: `keys` (filtered by field) is empty list.
            pass
        return value

    def to_text_relevant(self, lang):
        """Get the relevant text for this prompt.

        Args:
            :param lang: (str) The language.

        Returns:
            str: The text representation of the relevant.
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

        Args:
            lang (str): The language.
            numbered (bool): Should choice options be numbered?

        Returns:
            str: The text representation of the response entry field.
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
        #         # TODO: Fix read_only lookup.
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

        Args:
            lang (str): The language.

        Returns:
            str or dict: The representation of the entry field.
        """
        field = None
        if self.odktype in ['select_multiple', 'select_one']:
            field = self.choices.name_labels(lang=lang)
        elif self.odktype in OdkPrompt.response_types:
            field = '_' * 30 + '({})'.format(self.odktype)
        return field

    def to_text(self, lang):
        """Get the text representation of the full prompt.

        Args:
            lang (str): The language.

        Returns:
            str: The text from all parts of the prompt.
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

        Args:
            lang (str): The language.
            **bottom_border (bool): Renders a border at bottom of prompt. This
                is necessary for section headers followed by a group.

        Returns:
            dict: The text from all parts of the prompt.
        """
        # TODO: Refactor so that the dict row is only looped through once.
        prompt = self.format_media_labels(self.row)
        prompt = self.set_grouped_media_field(prompt)
        prompt = self.set_descriptive_metadata(prompt)
        prompt = self.reformat_default_lang_vars(prompt, lang)
        prompt = self.truncate_fields(prompt)
        prompt = self.reformat_double_line_breaks(prompt)

        prompt['input_field'] = self.to_html_input_field(lang)

        if self.is_section_header:
            prompt['is_section_header'] = True
        if 'bottom_border' in kwargs:
            prompt['bottom_border'] = True
        if 'preset' in kwargs:
            prompt = self.handle_preset(prompt, lang, kwargs['preset'])

        return prompt

    @staticmethod
    def html_options(**kwargs):
        """HTML options.

        Args:
            **kwargs (dict): Keyword arguments.

        Returns:
            dict: Modified settings based on keyword arguments.
        """
        if 'preset' not in kwargs:
            return kwargs
        for k, v in PRESETS[kwargs['preset']]['render_settings']['html']\
                .items():
            kwargs[k] = v
        return kwargs

    def to_html(self, lang, highlighting, **kwargs):
        """Convert to html.

        Args:
            lang (str): The language.
            highlighting (bool): For color highlighting of various components
                of html template.
            **kwargs: Arbitrary keyword arguments delegated fully to to_dict().

        Returns:
            str: A rendered html template.
        """
        settings = self.html_options(**kwargs)
        # pylint: disable=no-member
        return TEMPLATE_ENV.get_template('content/content-tr-base.html')\
            .render(question=self.to_dict(lang=lang, **settings),
                    highlighting=highlighting, **settings)
