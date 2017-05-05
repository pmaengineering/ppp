try:
    from error import OdkformError
except:
    try:
        from .error import OdkformError
    except:
        from pmix.error import OdkformError


class Odktable:
    """Class to represent a single ODK table from an XLSForm"""

    def __init__(self):
        """Initialize table object with empty data bin"""
        self.data = []

    def add(self, odkprompt):
        """Add a row of data from XLSForm

        :param odkprompt: (Odkprompt) ODK table row
        """
        self.data.append(odkprompt)

    def to_text(self, lang=None):
        """Get the text representation of the table

        :param lang: (str) The language
        :return: (str) The text for this table
        """
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
        #     these_choices = (choice_format.format(char) for _ in self.choices)
        #     these_labels = ' '.join(these_choices)
        #     option_labels.append(these_labels)
        #
        # full_prompts = (' '.join(i) for i in zip(prompt_labels, option_labels))
        # body = '\n'.join(full_prompts)
        # result = '\n'.join((choice_row, body))
        result = 'ODK TABLE TEXT'
        return result
