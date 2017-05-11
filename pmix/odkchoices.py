from pmix.error import OdkformError


class Odkchoices:
    """A class to represent a choice list defined in an XLSForm"""

    def __init__(self, list_name):
        """Initialize with a choice list name

        :param list_name: (str) The name of the choice list
        """
        self.list_name = list_name
        self.data = []

    def add(self, choice):
        """Add a choice to this choice list

        :param choice: A JSON row as parsed from the XLSForm
        """
        self.data.append(choice)

    def labels(self, lang=None):
        """Get the labels for this choice list in the desired language

        :param lang: (str) The language in which to return the choice labels
        :return: Correctly ordered list of choice labels
        """
        langs = self.langs()
        if lang and lang not in langs:
            m = 'Language "{}" not found in choice list {}'
            m = m.format(lang, self.list_name)
            raise OdkformError(m)
        elif not langs:
            m = 'No languages found in choice list {}'.format(self.list_name)
            raise OdkformError(m)

        if lang:
            lang_col = 'label::{}'.format(lang)
            labels = [d[lang_col] for d in self.data]
        else:
            first = langs[0]
            lang_col = 'label::{}'.format(first) if first else 'label'
            labels = [d[lang_col] for d in self.data]
        return labels

    def langs(self):
        """Discover all languages for these choices

        :return: Alphabetized list of languages
        """
        langs = set()
        for d in self.data:
            these_langs = set()
            for k in d:
                if k == 'label':
                    # Default language
                    these_langs.add('')
                elif k.startswith('label::'):
                    lang = k[len('label::'):]
                    these_langs.add(lang)
            if not langs:
                langs = these_langs
            elif langs != these_langs:
                m = 'In choice list {}, different languages found: {} and {}'
                m = m.format(self.list_name, langs, these_langs)
                raise OdkformError(m)
        lang_list = sorted(list(langs))
        return lang_list

    def __str__(self):
        s = '{}: {}'.format(self.list_name, self.labels())
        return s

    def __repr__(self):
        s = "<Odkchoices '{}(len: {})'>".format(self.list_name, len(self.data))
        return s
