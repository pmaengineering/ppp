from pmix.odktable import Odktable


class Odkgroup:
    """Class to represent a field-list group in XLSForm"""

    def __init__(self, opener):
        """Initialize a group"""
        self.opener = opener
        self.data = []
        self.pending_table = None

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

        :param row: (dict) Row from XLSForm
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

    def to_text(self, lang=None):
        """Get the text representation of the full group

        :param lang: (str) The language
        :return: (str) The text for this group
        """
        obj_texts = (d.to_text(lang) for d in self.data)
        sep = '\n\n{}\n\n'.format(' -' * 25)
        group_text = sep.join(obj_texts)
        return group_text

    def to_dict(self, lang=None):
        """Get the text representation of the full group

        :param lang: (str) The language.
        :return: (dict) The text for this group.
        """
        group_text = 'Group (temporary placeholder)'
        return group_text
