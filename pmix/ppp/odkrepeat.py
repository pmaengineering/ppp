"""Module for the OdkRepeat class."""
import textwrap
from pmix.ppp.config import TEMPLATE_ENV
from pmix.ppp.odkgroup import OdkGroup
from pmix.ppp.odkprompt import OdkPrompt
from pmix.ppp.odktable import OdkTable


class OdkRepeat:
    """Class to represent repeat construct from XLSForm."""

    def __init__(self, opener):
        """Initialize repeat object with empty data bin."""
        self.opener = opener
        self.data = []

    def __repr__(self):
        """Print representation of instance."""
        return "<OdkRepeat {}: {}>".format(self.opener['name'], self.data)

    def add(self, obj):
        """Add XLSForm object to repeat.

        Only other prompts and groups are allowed to be added.

        :param obj: either Odkgroup or Odkprompt.
        """
        self.data.append(obj)

    def to_text(self, lang):
        """Get the text representation of the entire repeat group.

        :param lang: (str) The language.
        :return: (str) The text for this repeat.
        """
        obj_texts = (d.to_text(lang) for d in self.data)
        sep = '\n\n{}\n\n'.format('=' * 50)
        repeat_text = sep.join(obj_texts)
        wrapped = textwrap.indent(repeat_text, '|  ', lambda x: True)
        return wrapped

    def to_html(self, lang, highlighting):
        """Get the html representation of the full group.

        :param lang: (str) The language.
        :param highlighting: (bool) Highlighting on/off.
        :return: (dict) The text for this group.
        """
        html = ''
        html += self.render_header(self.opener, lang, highlighting)
        for i in self.data:
            if isinstance(i, OdkPrompt):
                i.row['in_repeat'] = True
                html += i.to_html(lang, highlighting)
            elif isinstance(i, OdkGroup):
                i.in_repeat = True
                html += i.to_html(lang, highlighting)
            elif isinstance(i, OdkTable):
                i.in_repeat = True
                html += i.to_html(lang, highlighting)
        html += self.render_footer()
        return html

    @staticmethod
    def render_prompt(i, lang, highlighting):
        """Render prompt."""
        i.row['in_repeat'] = True
        return i.to_html(lang, highlighting)

    @staticmethod
    def render_header(i, lang, highlighting):
        """Render header."""
        # pylint: disable=no-member
        html = TEMPLATE_ENV.get_template('content/repeat/repeat-opener.html')\
            .render()
        i['simple_type'] = i['type']
        i['in_repeat'] = True
        i['is_repeat_header'] = True
        html += OdkPrompt(i).to_html(lang, highlighting)
        return html

    @staticmethod
    def render_footer():
        """Render footer."""
        # pylint: disable=no-member
        return TEMPLATE_ENV.get_template('content/repeat/repeat-closer.html')\
            .render()
