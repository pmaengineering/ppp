"""Abstract super class for other ODK XLSForm types."""


class OdkAbstractFormElement:
    """Abstract super class for other ODK XLSForm types."""

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
        """Return a console string representation."""
        return "<" + self.__class__.__name__ + " " + self.row["name"] + ">"
