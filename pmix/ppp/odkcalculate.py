"""Module for the OdkCalculate class."""


class OdkCalculate:
    """Class to represent a single ODK calculate from an XLSForm."""

    def __init__(self, row):
        """Initialize the XLSForm calculate, a single row."""
        self.row = row

    def to_html(self, *args, **kwargs):
        """Convert to html."""
        return ""

    def to_text(self, *args, **kwargs):
        """Convert to text."""
        return ""

    def __repr__(self):
        """Return a representation of this calculate."""
        return '<OdkCalculate {}>'.format(self.row['name'])
