"""Module for the OdkChoices class."""
from ppp.definitions.error import InvalidLanguageException


class OdkChoices:
    """A class to represent a choice list defined in an XLSForm.

    Attributes:
        list_name (str): The name of the choice list.
        data (list): A list of choice options for the choice list.

    """

    def __init__(self, list_name):
        """Initialize a choice list.

        Args:
            list_name (str): The name of the choice list.
        """
        self.list_name = list_name
        self.data = []

    def __repr__(self):
        """Print representation of instance."""
        return "<Odkchoices '{}(len: {})'>".format(self.list_name,
                                                   len(self.data))

    def __str__(self):
        """Convert instance to string."""
        return '{}: {}'.format(self.list_name, self.labels(lang='English'))

    def add(self, choice):
        """Add a choice to this choice list.

        Args:
            choice (dict): A single choice row.
        """
        self.data.append(choice)

    def labels(self, lang):
        """Get the labels for this choice list in the desired language.

        Args:
            lang (str): The language in which to return the choice labels.

        Returns:
            list: Correctly ordered list of choice labels.

        Raises:
            InvalidLanguageException
        """
        lang_col = 'label::{}'.format(lang) if lang else 'label'
        try:
            labels = [d[lang_col] for d in self.data]
            return labels
        except (KeyError, IndexError):
            msg = 'Language {} not found in choice list {}.'\
                .format(lang, self.list_name)
            raise InvalidLanguageException(msg)

    def name_labels(self, lang):
        """Get choice name labels.

        Args:
            lang (str): The language of choice list.

        Returns:
            list: Choice variable names and associated labels for choice list.
        """
        labels = self.labels(lang)
        return [{'name': row['name'], 'label': labels[i]} for i, row in
                enumerate(self.data)]

    def choice_langs(self):
        """Discover all languages for these choices.

        Returns:
            list: Alphabetized list of languages.

        Raises:
            InvalidLanguageException: If languages of first row differ from
                languages in any other row.
        """
        langs = set()
        for datum in self.data:
            these_langs = set()
            for k in datum:
                if k == 'label':
                    these_langs.add('')  # Default language
                elif k.startswith('label::'):
                    lang = k[len('label::'):]
                    these_langs.add(lang)
            if not langs:
                langs = these_langs
            elif langs != these_langs:
                msg = 'In choice list {}, different languages found: {} and {}'
                msg = msg.format(self.list_name, langs, these_langs)
                raise InvalidLanguageException(msg)
        lang_list = sorted(list(langs))
        return lang_list
