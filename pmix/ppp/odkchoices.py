"""Module for the OdkChoices class."""
from pmix.ppp.error import InvalidLanguageException


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
            InvalidLanguageException: Language parameter not found in choice
                list.
            InvalidLanguageException: No languages found in choice list.
        """
        choice_langs = self.choice_langs()
        if lang not in choice_langs:
            msg = 'Language "{}" not found in choice list {}'
            msg = msg.format(lang, self.list_name)
            raise InvalidLanguageException(msg)
        elif not choice_langs:
            msg = 'No languages found in choice list {}'.format(self.list_name)
            raise InvalidLanguageException(msg)

        if lang:
            lang_col = 'label::{}'.format(lang)
        else:
            default_language = 'English'
            lang_col = 'label::{}'.format(default_language) \
                if default_language else 'label'
        labels = [d[lang_col] for d in self.data]
        return labels

    def name_labels(self, lang):
        """Get choice name labels.

        Args:
            lang (str): The language of choice list.

        Returns:
            list: Choice variable names and associated labels for choice list.
        """
        # 1. 'label' / all language fields alone needs to be supported if no
        # default language specified in form and no language passed.
        #  * Whatever language is determined needs to be consistent.
        # 2. if no default language and no language passed, we need to
        # determine what the default language is. And there needs to be
        # consistency between worksheets.
        # 3. if language is passed or there is a default language, need to
        # throw an error here if there is no label::<language> field.
        #  * Unit test to make sure that the invalidlanguageexception fires for
        #  the form "InvalidLanguage_FQ".
        try:
            return [{'name': x['name'], 'label': x['label::{}'.format(lang)]}
                    for x in self.data]
        except KeyError:
            raise InvalidLanguageException

    def choice_langs(self):
        """Discover all languages for these choices.

        Returns:
            list: Alphabetized list of languages.

        Raises:
            InvalidLanguageException: If choice languages differe from survey
                languages.
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
