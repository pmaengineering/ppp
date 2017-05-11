import textwrap


class Odkrepeat:
    """Class to represent repeat construct from XLSForm"""

    def __init__(self, opener, output_format):
        """Initialize repeat object with empty data bin"""
        self.opener = opener
        self.output_format = output_format
        self.data = []

    def add(self, obj):
        """Add XLSForm object to repeat

        Only other prompts and groups are allowed to be added.

        :param obj: either Odkgroup or Odkprompt
        """
        self.data.append(obj)

    def to_text(self, lang=None):
        """Get the text representation of the entire repeat group

        :param lang: (str) The language
        :return: (str) The text for this repeat
        """
        obj_texts = (d.to_text(lang) for d in self.data)
        sep = '\n\n{}\n\n'.format('=' * 50)
        repeat_text = sep.join(obj_texts)
        wrapped = textwrap.indent(repeat_text, '|  ', lambda x: True)
        return wrapped

    def to_dict(self, lang=None):
        """Get the text representation of the entire repeat group

        :param lang: (str) The language.
        :return: (dict) The text for this repeat.
        """
        wrapped = 'Repeat (temporary placeholder)'
        return wrapped
