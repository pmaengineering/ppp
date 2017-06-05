#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OdkGroup."""

from pmix.ppp.odkprompt import OdkComponent, OdkPrompt
from pmix.ppp.config import TEMPLATE_ENV
from pmix.ppp.odktable import OdkTable


class OdkGroup:
    """Class to represent a field-list group in XLSForm."""

    def __init__(self, opener):
        """Initialize a group."""
        self.opener = opener
        self.data = []
        self.pending_table = None
        self.in_repeat = False

    def __repr__(self):
        """Printed representation."""
        return "<OdkGroup {}: {}>".format(self.opener['name'], self.data)

    def add(self, row):
        """Add a row of data from XLSForm.

        This method should not be called if row comes from an ODK table.

        :param row: (dict) Row from XLSForm.
        """
        self.add_pending()
        self.data.append(row)

    def add_table(self, odkprompt):
        """Add a row of a table object to the group.

        This method should only be called for rows from an ODK table.

        :param odkprompt: (dict) Prompt ow from XLSForm.
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
        """Get the text representation of the full group.

        :param lang: (str) The language.
        :return: (str) The text for this group.
        """
        obj_texts = (d.to_text(lang) for d in self.data)
        sep = '\n\n{}\n\n'.format(' -' * 25)
        group_text = sep.join(obj_texts)
        return group_text

    @staticmethod
    def render_header(i, lang, highlighting):
        """Render header."""
        i['in_group'] = True
        i['simple_type'] = i['type']
        i['is_group_header'] = True
        return OdkPrompt(i).to_html(lang, highlighting)

    @staticmethod
    def render_footer(i, lang, highlighting):
        """Render footer."""
        i.row['in_group'] = True
        return i.to_html(lang, highlighting)

    @staticmethod
    def render_prompt(i, lang, highlighting):
        """Render prompt."""
        i.row['in_group'] = True
        return i.to_html(lang, highlighting)

    def to_html(self, lang, highlighting):
        """Get the html representation of the full group.

        :param lang: (str) The language.
        :param highlighting: (bool) Highlighting on/off.
        :return: (dict) The text for this group.
        """
        html = ''
        # pylint: disable=no-member
        html += TEMPLATE_ENV.get_template('content/group/group-opener.html')\
            .render()
        html += self.render_header(self.opener, lang, highlighting)
        for i in self.data[0:-1]:
            if isinstance(i, OdkPrompt):
                i.row['in_repeat'] = self.in_repeat
                html += self.render_prompt(i, lang, highlighting)
            elif isinstance(i, OdkTable):
                i.in_repeat = self.in_repeat
                html += i.to_html(lang, highlighting)
        if isinstance(self.data[-1], OdkPrompt):
            self.data[-1].row['in_repeat'] = self.in_repeat
            html += self.render_footer(self.data[-1], lang, highlighting)
        if isinstance(self.data[-1], OdkTable):
            self.data[-1].in_repeat = self.in_repeat
            html += self.data[-1].to_html(lang, highlighting)
        # pylint: disable=no-member
        html += TEMPLATE_ENV.get_template('content/group/group-closer.html')\
            .render()
        return html
