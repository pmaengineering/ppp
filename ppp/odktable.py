"""Module for the OdkTable class."""
from ppp.config import TEMPLATE_ENV
from ppp.definitions.utils import exclusion
# from ppp.definitions.error import OdkformError


class OdkTable:
    """Class to represent a single ODK table from an XLSForm.

    Attributes:
        data (list): List of 1 OdkPrompt header and 1+ OdkPrompt rows.
        header (OdkPrompt): OdkPrompt representing table header.
        contents (list): List of OdkPrompts consisting of table rows.
        in_repeat (bool): Is this table part of a repeat group?
    """

    def __init__(self):
        """Initialize table object with empty initial values."""
        self.data = []
        self.header = None
        self.contents = None
        self.in_repeat = False

    def __repr__(self):
        """Print representation of instance."""
        return '<OdkTable w/ Header \'{}\': {}>'\
            .format(self.data[0].row['name'], self.data)

    def add(self, odkprompt):
        """Add a row of data from XLSForm.

        Args:
            odkprompt (OdkPrompt): ODK table row.
        """
        self.data.append(odkprompt)

    @staticmethod
    def format_row(prompt, lang, **kwargs):
        """Format rows row based on HTML options determined by kwargs.

        Args:
            prompt (OdkPrompt): The row.
            lang (str): The language.
            **kwargs: Keyword arguments.

        Returns:
            dict: Reformatted row.
        """
        settings = prompt.html_options(**kwargs)
        table_row = prompt.to_dict(lang=lang, **settings)
        return table_row

    def set_header_and_contents(self, lang, **kwargs):
        """Set header and contents of table.

        Args:
            lang (str): The language.
            **kwargs: Keyword arguments
        """
        for i in self.data:
            i.row['in_group'] = True
            i.row = self.format_row(prompt=i, lang=lang, **kwargs)
        self.header = self.data[0]
        self.contents = self.data[1:]

        # - De-list labels
        for con in self.contents:
            con.row['label'] = con.row['label'][0]

    # Temporary noinspection until method is added.
    # noinspection PyUnusedLocal
    @staticmethod
    def to_text():
        """Get the text representation of the table."""
        # def to_text(self, lang):
        # """Get the text representation of the table.
        #
        # Args:
        #     lang (str): The language.
        # Returns:
        #     str: The text for this table.
        #
        # """
        # choices = pmix.utils.d(self.choices, lang)
        #
        # choice_width = max(len(c) for c in self.choices)
        # prompt_width = max(len(p) for p in self.prompts)
        #
        # choice_format = '{:>{}}'.format(choice_width)
        # choice_labels = (choice_format.format(c) for c in self.choices)
        # choice_row = ' '.join((' ' * prompt_width, choice_labels))
        #
        # prompt_format = '{:<{}}'.format(prompt_width)
        # prompt_labels = (prompt_format.format(p) for p in self.prompts)
        #
        # option_labels = []
        # for prompt in self.prompts:
        #     if prompt.odktype == 'select_one':
        #         char = '*'
        #     elif prompt.odktype == 'select_multiple':
        #         char = '_'
        #     else:
        #         m = 'Unexpected type in ODK table: {}'.format(prompt.odktype)
        #         raise OdkformError(m)
        #     these_choices = (choice_format.format(char) for _
        # in self.choices)
        #     these_labels = ' '.join(these_choices)
        #     option_labels.append(these_labels)
        #
        # full_prompts = (' '.join(i) for i in zip(prompt_labels,
        # option_labels))
        # body = '\n'.join(full_prompts)
        # result = '\n'.join((choice_row, body))
        result = 'ODK TABLE TEXT'  # Placeholder
        return result

    def to_html(self, lang, highlighting, **kwargs):
        """Convert to html.

        Args:
            lang (place): The language.
            highlighting (bool): Displays highlighted sub-sections if True.
            **kwargs: Keyword arguments.

        Returns:
            str: A rendered html template.
        """
        # - Render header
        self.set_header_and_contents(lang, **kwargs)
        table = list()
        table.append(self.header.row)

        # - Render body
        for i in self.contents:
            if exclusion(item=i, settings=kwargs):
                continue

            table.append(i.row)

        # pylint: disable=no-member
        return TEMPLATE_ENV.get_template('content/table/table.html')\
            .render(table=table, lang=lang, highlighting=highlighting,
                    **kwargs)
