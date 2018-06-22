"""Module for the OdkChoices class."""
from ppp.definitions.error import InvalidLanguageException
from ppp.definitions.constants import CHOICE_NAME_VARIATIONS


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
        label_variations = ['label']
        if lang:
            label_variations += \
                [x.format(lang) for x in ('label::{}', 'label:{}')]
        try:
            for label in label_variations:
                if label in self.data[0]:
                    return [d[label] for d in self.data]
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
        rows = enumerate(self.data)
        labels = self.labels(lang)
        formatted_rows = []
        for i, row in rows:
            formatted_row = {'label': labels[i]}
            for x in CHOICE_NAME_VARIATIONS:
                if x in row:
                    formatted_row[x] = row[x]
            formatted_rows.append(formatted_row)
        return formatted_rows

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
                elif k.startswith('label:'):
                    lang = k[len('label:'):]
                    these_langs.add(lang)
            if not langs:
                langs = these_langs
            elif langs != these_langs:
                msg = 'In choice list {}, different languages found: {} and {}'
                msg = msg.format(self.list_name, langs, these_langs)
                raise InvalidLanguageException(msg)
        lang_list = sorted(list(langs))
        return lang_list
