"""Module for the OdkRepeat class."""
import textwrap
# from ppp.config import TEMPLATE_ENV
from ppp.config import get_template_env
from ppp.odkgroup import OdkGroup, set_template_env as odkgroup_template
from ppp.odkprompt import OdkPrompt, set_template_env as odkpromt_template
from ppp.odktable import OdkTable, set_template_env as odktable_template
from ppp.definitions.utils import exclusion

TEMPLATE_ENV = None


def set_template_env(template):
    """Set template env"""
    global TEMPLATE_ENV
    TEMPLATE_ENV = get_template_env(template)
    odkgroup_template(template)
    odkpromt_template(template)
    odktable_template(template)


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
    def render_header(i, lang, **kwargs):
        """Render repeat group header.

        A repeat group header consists of some opening html tags, followed by
        an OdkPrompt with a few extra attributes.

        Args:
            i (dict): A dictionary row representing first row of repeat group.
            lang (str): The language.


            **kwargs: Keyword arguments.

        Returns:
            str: A rendered html representation of repeat group header.
        """
        # pylint: disable=no-member
        html = TEMPLATE_ENV.get_template('content/repeat/repeat-opener.html')\
            .render(**kwargs, settings=kwargs)
        i['simple_type'] = i['type']
        i['in_repeat'] = True
        i['is_repeat_header'] = True
        html += OdkPrompt(i).to_html(lang, **kwargs, settings=kwargs)
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

    def to_html(self, lang, **kwargs):
        """Convert repeat group components to html and return concatenation.

        Args:
            lang (str): The language.


            **kwargs: Keyword arguments.

        Returns:
            str: A rendered html concatenation of component templates.
        """
        html = ''

        # - Render header
        html += self.render_header(self.opener, lang, **kwargs)

        # - Render body
        for i in self.data:
            if exclusion(item=i, settings=kwargs):
                continue

            if isinstance(i, OdkPrompt):
                i.row['in_repeat'] = True
                html += i.to_html(lang, **kwargs)
            elif isinstance(i, OdkGroup):
                i.in_repeat = True
                html += i.to_html(lang, **kwargs)
            elif isinstance(i, OdkTable):
                i.in_repeat = True
                # - Render footer
                html += i.to_html(lang, **kwargs)
        html += self.render_footer()

        return html
