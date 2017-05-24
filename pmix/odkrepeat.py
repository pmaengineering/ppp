from jinja2 import Environment, PackageLoader
import textwrap


class OdkRepeat:
    """Class to represent repeat construct from XLSForm"""

    def __init__(self, opener):
        """Initialize repeat object with empty data bin"""
        self.opener = opener
        self.data = []

    def add(self, obj):
        """Add XLSForm object to repeat

        Only other prompts and groups are allowed to be added.

        :param obj: either Odkgroup or Odkprompt
        """
        self.data.append(obj)

    def to_text(self, lang):
        """Get the text representation of the entire repeat group

        :param lang: (str) The language
        :return: (str) The text for this repeat
        """
        obj_texts = (d.to_text(lang) for d in self.data)
        sep = '\n\n{}\n\n'.format('=' * 50)
        repeat_text = sep.join(obj_texts)
        wrapped = textwrap.indent(repeat_text, '|  ', lambda x: True)
        return wrapped

    def to_dict(self, lang):
        """Get the text representation of the entire repeat group

        :param lang: (str) The language.
        :return: (dict) The text for this repeat.
        """
        wrapped = 'Repeat (temporary placeholder)'
        return wrapped

    def to_html(self, lang, highlighting):
        env = Environment(loader=PackageLoader('pmix'))
        question = env.get_template('content/content-tr-base.html').render(question=self.to_dict(lang=lang),
                                                                              highlighting=highlighting)
        return question
