"""Module for the OdkRepeat class."""
import textwrap
from pmix.ppp.config import TEMPLATE_ENV
from pmix.ppp.odkgroup import OdkGroup
from pmix.ppp.odkprompt import OdkPrompt
from pmix.ppp.odktable import OdkTable


class OdkRepeat:
    """Class to represent repeat construct from XLSForm.

    Attributes:
        opener (dict): A dictionary row representing first row of repeat group.
        data (list): A list of repeat group components.

    """

    def __init__(self, opener):
        """Initialize a repeat group.

        Args:
            opener (dict): A dictionary row representing first row of group.
                In ODK Specification, this would be of 'begin repeat' type.
        """
        self.opener = opener
        self.data = []

    def __repr__(self):
        """Print representation of instance."""
        return "<OdkRepeat {}: {}>".format(self.opener['name'], self.data)

    @staticmethod
    def render_header(i, lang, highlighting):
        """Render repeat group header.

        A repeat group header consists of some opening html tags, followed by
        an OdkPrompt with a few extra attributes.

        Args:
            i (dict): A dictionary row representing first row of repeat group.
            lang (str): The language.
            highlighting (bool): For color highlighting of various components
                of html template.

        Returns:
            str: A rendered html representation of repeat group header.
        """
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
        """Render repeat group footer.

        A repeat group footer consists of some closing html tags.

        Returns:
            str: A rendered html representation of repeat group footer.
        """
        # pylint: disable=no-member
        return TEMPLATE_ENV.get_template('content/repeat/repeat-closer.html')\
            .render()

    def add(self, obj):
        """Add XLSForm object to repeat.

        Only other prompts and groups are allowed to be added.

        Args:
            obj (OdkPrompt or OdkGroup): Item to add.
        """
        self.data.append(obj)

    def to_text(self, lang):
        """Get the text representation of the entire repeat group.

        Args:
            lang (str): The language

        Returns:
            str: The text for this repeat.
        """
        obj_texts = (d.to_text(lang) for d in self.data)
        sep = '\n\n{}\n\n'.format('=' * 50)
        repeat_text = sep.join(obj_texts)
        wrapped = textwrap.indent(repeat_text, '|  ', lambda x: True)
        return wrapped

    # TODO: Finish this or change debug feature.
    # def to_dict(self, lang):
    #     """Format components of a repeat.
    #
    #     Args:
    #         lang (str): The language.
    #
    #     Returns:
    #         list: A list of reformatted components.
    #
    #     """
    #     repeat = []
    #     return repeat

    def to_html(self, lang, highlighting):
        """Convert repeat group components to html and return concatenation.

        Args:
            lang (str): The language.
            highlighting (bool): For color highlighting of various components
                of html template.

        Returns:
            str: A rendered html concatenation of component templates.
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
