"""Module for the OdkChoices class."""
from pmix.error import OdkformError


class OdkChoices:
    """A class to represent a choice list defined in an XLSForm."""

    def __init__(self, list_name):
        """Initialize with a choice list name.

        :param list_name: (str) The name of the choice list.
        """
        self.list_name = list_name
        self.data = []

    def add(self, choice):
        """Add a choice to this choice list.

        :param choice: A JSON row as parsed from the XLSForm.
        """
        self.data.append(choice)

    def labels(self, lang):
        """Get the labels for this choice list in the desired language.

        :param lang: (str) The language in which to return the choice labels.
        :return: Correctly ordered list of choice labels.
        """
        choice_langs = self.choice_langs()
        if lang not in choice_langs:
            msg = 'Language "{}" not found in choice list {}'
            msg = msg.format(lang, self.list_name)
            raise OdkformError(msg)
        elif not choice_langs:
            msg = 'No languages found in choice list {}'.format(self.list_name)
            raise OdkformError(msg)

        if lang:
            lang_col = 'label::{}'.format(lang)
        else:
            default_language = 'English'
            lang_col = 'label::{}'.format(default_language) \
                if default_language else 'label'
        labels = [d[lang_col] for d in self.data]
        return labels

    def name_labels(self, lang):
        """Get choice name labels."""
        return [{'name': x['name'], 'label': x['label::{}'.format(lang)]}
                for x in self.data]

    def choice_langs(self):
        """Discover all languages for these choices.

        :return: Alphabetized list of languages.
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
                raise OdkformError(msg)
        lang_list = sorted(list(langs))
        return lang_list

    def __str__(self):
        """String conversion of instance."""
        return '{}: {}'.format(self.list_name, self.labels(lang='English'))

    def __repr__(self):
        """Print representation of instance."""
        return "<Odkchoices '{}(len: {})'>".format(self.list_name,
                                                   len(self.data))
