from pmix.ppp_config import template_env
from pmix.odkprompt import OdkComponent, OdkPrompt
from pmix.odktable import OdkTable


class OdkGroup:
    """Class to represent a field-list group in XLSForm"""

    def __init__(self, opener):
        """Initialize a group"""
        self.opener = opener
        self.data = []
        self.pending_table = None
        self.header = self.set_header()
        self.footer = self.set_footer()
        self.in_repeat = False

    def __repr__(self):
        s = "<OdkGroup {}: {}>".format(self.opener['name'], self.data)
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
            self.pending_table = OdkTable()
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

    def render_header(self, input, lang, highlighting):
        input['in_group'] = True
        input['simple_type'] = input['type']
        input['is_group_header'] = True
        return OdkPrompt(input).to_html(lang, highlighting)

    def render_footer(self, input, lang, highlighting):
        input.row['in_group'] = True
        # input.row['is_group_footer'] = True
        return input.to_html(lang, highlighting)

    def render_prompt(self, input, lang, highlighting):
        input.row['in_group'] = True
        return input.to_html(lang, highlighting)

    def to_html(self, lang, highlighting):
        """Get the html representation of the full group.

        :param lang: (str) The language.
        :param highlighting: (bool) Highlighting on/off.
        :return: (dict) The text for this group.
        """

        s = ''
        s += template_env.get_template('content/group/group-opener.html').render()
        s += self.render_header(self.opener, lang, highlighting)
        for i in self.data[0:-1]:
            if isinstance(i, OdkPrompt):
                i.row['in_repeat'] = self.in_repeat
                s += self.render_prompt(i, lang, highlighting)
            elif isinstance(i, OdkTable):
                i.in_repeat = self.in_repeat
                s += i.to_html(lang, highlighting)
        if isinstance(self.data[-1], OdkPrompt):
            self.data[-1].row['in_repeat'] = self.in_repeat
            s += self.render_footer(self.data[-1], lang, highlighting)
        if isinstance(self.data[-1], OdkTable):
            self.data[-1].in_repeat = self.in_repeat
            s += self.data[-1].to_html(lang, highlighting)
        s += template_env.get_template('content/group/group-closer.html').render()
        return s


class OdkGroupHeader(OdkComponent):
    """Class to represent a 'begin group' line of XLSForm, and a group header in paper form."""

    def __init__(self, opener):
        """Initialize a group header."""
        OdkComponent.__init__(self)
        self.data = opener

    def __repr__(self):
        s = "<OdkGroupHeader: {}>".format(self.data)
        return s

    def to_dict(self, lang):
        self.data = self.reformat_default_language_variable_names(self.data, lang)
        self.data = self.truncate_fields(self.data)
        self.data['is_group_header'] = True
        return self.data

    def to_html(self, lang, highlighting):

        return template_env.get_template('content/content-tr-base.html').render(question=self.to_dict(lang=lang),
                                                                       highlighting=highlighting)


class OdkGroupFooter:
    """Class to represent a 'begin group' line of XLSForm, and a group header in paper form."""

    def __init__(self, opener):
        """Initialize a group header."""
        self.data = opener

    def __repr__(self):
        s = "<OdkGroupFooter: {}>".format(self.data)
        return s

    def to_dict(self, lang):
        self.data['is_group_footer'] = True
        return self.data

    def to_html(self, lang, highlighting):
        return template_env.get_template('content/content-tr-base.html').render(question=self.to_dict(lang),
                                                                       highlighting=highlighting)
