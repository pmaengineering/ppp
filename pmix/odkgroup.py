from jinja2 import Environment, PackageLoader
from pmix.odkprompt import OdkComponent
from pmix.odktable import Odktable


class Odkgroup:
    """Class to represent a field-list group in XLSForm"""

    def __init__(self, opener):
        """Initialize a group"""
        self.opener = opener
        self.data = []
        self.pending_table = None
        self.header = self.set_header()
        self.footer = self.set_footer()

    def __repr__(self):
        s = "<Odkgroup {}: {}>".format(self.opener['name'], self.data)
        return s

    def add(self, row):
        """Add a row of data from XLSForm

        This method should not be called if row comes from an ODK table

        :param row: (dict) Row from XLSForm
        """
        self.add_pending()
        self.data.append(row)

    def add_table(self, odkprompt):
        """Add a row of a table object to the group

        This method should only be called for rows from an ODK table

        :param odkprompt: (dict) Prompt ow from XLSForm.
        """
        if self.pending_table:
            self.pending_table.add(odkprompt)
        else:
            self.pending_table = Odktable()
            self.pending_table.add(odkprompt)

    def add_pending(self):
        """Add table to group data if one is in being built"""
        if self.pending_table:
            self.data.append(self.pending_table)
            self.pending_table = None

    def set_header(self):
        data = self.opener
        return OdkGroupHeader(data)

    def set_footer(self):
        data = self.opener
        return OdkGroupFooter(data)

    def to_text(self, lang):
        """Get the text representation of the full group

        :param lang: (str) The language
        :return: (str) The text for this group
        """
        obj_texts = (d.to_text(lang) for d in self.data)
        sep = '\n\n{}\n\n'.format(' -' * 25)
        group_text = sep.join(obj_texts)
        return group_text

    def to_dict(self, lang):
        """Get the text representation of the full group

        :param lang: (str) The language.
        :return: (dict) The text for this group.
        """
        # TODO: Determine if to_dict and _to_Html methods are useful at all.
        group_text = 'Group (temporary placeholder)'
        return group_text

    def to_html(self, lang, highlighting):
        env = Environment(loader=PackageLoader('pmix'))
        question = env.get_template('content/content-tr-base.html').render(question=self.to_dict(lang=lang),
                                                                           highlighting=highlighting)
        return question


class OdkGroupHeader(OdkComponent):
    """Class to represent a 'begin group' line of XLSForm, and a group header in paper form."""

    def __init__(self, opener):
        """Initialize a group header."""
        OdkComponent.__init__(self)
        self.data = opener

    def to_dict(self, lang):
        self.data = self.reformat_default_language_variable_names(self.data, lang)
        self.data = self.truncate_fields(self.data)
        self.data['is_group_header'] = True
        return self.data

    def to_html(self, lang, highlighting):
        env = Environment(loader=PackageLoader('pmix'))
        question = env.get_template('content/content-tr-base.html').render(question=self.to_dict(lang=lang),
                                                                           highlighting=highlighting)
        return question


class OdkGroupFooter:
    """Class to represent a 'begin group' line of XLSForm, and a group header in paper form."""

    def __init__(self, opener):
        """Initialize a group header."""
        self.data = opener

    def to_dict(self):
        self.data['is_group_footer'] = True
        return self.data

    def to_html(self, lang, highlighting):
        env = Environment(loader=PackageLoader('pmix'))
        question = env.get_template('content/content-tr-base.html').render(question=self.to_dict(),
                                                                           highlighting=highlighting)
        return question
