"""Module for the OdkGroup class."""
# from ppp.config import TEMPLATE_ENV
from ppp.config import get_template_env
from ppp.odkprompt import OdkPrompt, set_template_env as odkpromt_template
from ppp.odktable import OdkTable, set_template_env as odktable_template
from ppp.definitions.utils import exclusion

TEMPLATE_ENV = None


def set_template_env(template):
    """Set template env."""
    global TEMPLATE_ENV
    TEMPLATE_ENV = get_template_env(template)
    odktable_template(template)
    odkpromt_template(template)


class OdkGroup:
    """Class to represent a field-list group in XLSForm.

    Attributes:
        opener (dict): A dictionary row representing first row of group.
        data (list): A list of group components.
        pending_table (OdkTable): A variable for storing an OdkTable object as
            it is being constructed.
        in_repeat (bool): Is this group part of a repeat group?
    """

    def __init__(self, opener):
        """Initialize a group.

        Args:
            opener (dict): A dictionary row representing first row of group.
                In ODK Specification, this would be of 'begin group' type.
        """
        self.opener = opener
        self.data = []
        self.pending_table = None
        self.in_repeat = False

    def __repr__(self):
        """Print representation."""
        return "<OdkGroup {}: {}>".format(self.opener['name'], self.data)

    @staticmethod
    def format_header(header):
        """Render group header.

        A group header is an OdkPrompt with a few extra attributes. Header is
        formatted and returned before initializating as an OdkPrompt.

        Args:
            header (dict): A dictionary row representing first row of group.

        Returns:
            dict: A reformatted representation.
        """
        header['in_group'] = True
        header['simple_type'] = header['type']
        header['is_group_header'] = True
        return header

    def add(self, row):
        """Add a row of data from XLSForm.

        This method should not be called if row comes from an ODK table.

        Args:
            row (dict): Row from XLSForm.
        """
        self.add_pending()
        self.data.append(row)

    def add_table(self, odkprompt):
        """Add a row of a table object to the group.

        This method should only be called for rows from an ODK table.

        Args:
            odkprompt (OdkPrompt): Row from XLSForm.
        """
        if self.pending_table:
            self.pending_table.add(odkprompt)
        else:
            self.pending_table = OdkTable()
            self.pending_table.add(odkprompt)

    def add_pending(self):
        """Add table to group data if one is in being built."""
        if self.pending_table:
            self.data.append(self.pending_table)
            self.pending_table = None

    def to_text(self, lang):
        """Get the text representation of the detailed group.

        Args:
            lang (str): The language.

        Returns:
            str: The text for this group.
        """
        obj_texts = (d.to_text(lang) for d in self.data)
        sep = '\n\n{}\n\n'.format(' -' * 25)
        group_text = sep.join(obj_texts)
        return group_text

    def to_html(self, lang, **kwargs):
        """Convert group components to html and return concatenation.

        Args:
            lang (str): The language.

        Returns:
            str: A rendered html concatenation of component templates.
        """
        html = ''
        # pylint: disable=no-member

        # - Render header
        html += TEMPLATE_ENV.get_template('content/group/group-opener.html')\
            .render(**kwargs, settings=kwargs)
        header = self.format_header(self.opener)

        html += OdkPrompt(header).to_html(lang, **kwargs)

        # - Render body
        for i in self.data:
            if exclusion(item=i, settings=kwargs):
                continue

            if isinstance(i, OdkPrompt):
                i.row['in_repeat'] = self.in_repeat
                i.row['in_group'] = True
                html += i.to_html(lang, **kwargs)
            elif isinstance(i, OdkTable):
                i.in_repeat = self.in_repeat
                html += i.to_html(lang, **kwargs)

        # - Render footer
        # pylint: disable=no-member
        html += TEMPLATE_ENV.get_template('content/group/group-closer.html')\
            .render(**kwargs, settings=kwargs)

        return html
