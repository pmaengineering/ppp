"""Module for the OdkPrompt class."""
from ppp.config import get_template_env
from ppp.definitions.constants import (
    TRUNCATABLE_FIELDS,
    LANGUAGE_DEPENDENT_FIELDS,
    LANGUAGE_DEPENDENT_FIELDS_NONMEDIA_FIELDS,
    TEMPLATES,
    IGNORE_RELEVANT_TOKEN,
    RELEVANCE_FIELD_TOKENS,
    PPP_REPLACEMENTS_FIELDS,
)
from ppp.odkabstractformelement import OdkAbstractFormElement

TEMPLATE_ENV = None


def set_template_env(template):
    """Set template env."""
    global TEMPLATE_ENV
    TEMPLATE_ENV = get_template_env(template)


class OdkAbstractPrompt(OdkAbstractFormElement):
    """Class to represent a single ODK prompt from an XLSForm.

    This is described in a single row of an XLSForm.

    Attributes:
        row (dict): A dictionary representation of prompt.
        odktype (str): The value corresponding to the prompts ODK type.
        is_section_header (bool): Designates whether or not the prompt is a
            section header.

    """

    def __init__(self, row):
        """Initialize the XLSForm prompt (a single row of a specific type).

        Args:
            row (dict): XLSForm headers as keys, row entries as values. It is
                guaranteed to have the "simple_type" key with a value from the
                class member variables `select_types`, `visible_response_types`, or
                `visible_non_response_types`.
        """
        super().__init__(row)
        self.odktype = self.row["simple_type"]
        self.is_section_header = True if self.row["name"].startswith("sect_") else False

    @staticmethod
    def truncate_text(text):
        """Truncate text and add an ellipsis when text is too long.

        Args:
            text (str): The text.

        Returns:
            str: Truncated text.
        """
        if len(text) > 100:
            text = text[0:98] + " …"
        return text

    @staticmethod
    def _reformat_double_line_breaks(row):
        """Convert labels and hints from strings to lists.

        This conversion process allows for line breaks to be rendered properly
        in html.

        Args:
            row (dict): The dictionary representation of prompt.

        Returns:
            dict: Reformatted representation.
        """
        for k, v in row.items():
            if True in [
                k.startswith(x) for x in LANGUAGE_DEPENDENT_FIELDS_NONMEDIA_FIELDS
            ]:
                if v:
                    row[k] = v.split("\n\n")
        return row

    @staticmethod
    def _reformat_default_lang_vars(row, lang):
        """Reformat default language variables.

        Reformat '::/:<language_name>' style variable names to remove the
        '::/:<language_name>', leaving just the variable.

        Args:
            row (dict): The dictionary representation of prompt.
            lang (str): The language.

        Returns:
            dict: Reformatted representation.
        """
        new_row = row.copy()
        if lang:
            for field in LANGUAGE_DEPENDENT_FIELDS:
                if field + "::" + lang in new_row:
                    new_row[field] = new_row[field + "::" + lang]
                elif field + ":" + lang in new_row:
                    new_row[field] = new_row[field + ":" + lang]
        return new_row

    def _truncate_fields(self, row):
        """Call truncate_text() method for all truncatable fields in component.

        Args:
            row (dict): The dictionary representation of prompt.

        Returns:
            dict: Reformatted representation of prompt.
        """
        new_row = row.copy()
        for field in TRUNCATABLE_FIELDS:
            if field in new_row:
                new_row[field + "_original"] = new_row[field]
                new_row[field] = self.truncate_text(new_row[field])
        return new_row

    @staticmethod
    def _ignore_relevant(prompt):
        """If applicable, ignores relevant, setting it to an empty string.

         In cases where a template is used which makes use of human-readable
         relevants via the ppp_relevant::<language> field of an XlsForm, this
         function looks for any IGNORE_RELEVANT_TOKEN present in the field and,
         if present, sets it to an empty string.

        Args:
            prompt (dict): Dictionary representation of prompt.

        Returns
            dict: Reformatted representation.
        """
        for x in RELEVANCE_FIELD_TOKENS:
            if x in prompt:
                if prompt[x] == IGNORE_RELEVANT_TOKEN:
                    prompt[x] = ""
        return prompt

    @staticmethod
    def _set_descriptive_metadata(prompt):
        """Set descriptive metadata.

        Args:
            prompt (dict): Dictionary representation of prompt.

        Returns
            dict: Reformatted representation.
        """
        prompt["is_section"] = False
        if prompt["simple_type"] == "note" and prompt["name"].startswith("sect_"):
            prompt["is_section"] = True
        return prompt

    @staticmethod
    def handle_template_presets(prompt, lang, template):
        """Handle template presets.

        Args:
            prompt (dict): Dictionary representation of prompt.
            lang (str): The language.
            template (str): The template name supplied.

        Returns
            dict: Reformatted representation.
        """
        # TODO: (jef 2017.09.24) Human readable: hint variables.
        # TODO: (jef 2017.09.24) Human readable: choice filters, calcs.
        for key in prompt:
            for exclusion in TEMPLATES[template]["field_exclusions"]:
                if key.startswith(exclusion):
                    prompt[key] = ""
                    continue

            if lang:
                for to_replace in TEMPLATES[template]["field_replacements"]:
                    replace_withs = [
                        "ppp_" + to_replace + "::" + lang,
                        "ppp_" + to_replace + ":" + lang,
                    ]
                    for replace_with in replace_withs:
                        if key == replace_with and prompt[replace_with]:
                            for x in PPP_REPLACEMENTS_FIELDS:
                                if to_replace.startswith(x):
                                    if x == "label":
                                        prompt[to_replace] = [prompt[replace_with]]
                                    elif x in RELEVANCE_FIELD_TOKENS:
                                        prompt[to_replace] = prompt[replace_with]

            if "choice names" in TEMPLATES[template]["other_specific_exclusions"]:
                if key == "input_field" and prompt["simple_type"] in (
                    "select_one",
                    "select_multiple",
                ):
                    prompt["input_field"] = [
                        {"name": "", "value": "", "label": i["label"]}
                        for i in prompt["input_field"]
                    ]

        OdkAbstractPrompt._ignore_relevant(prompt)

        return prompt

    def text_field(self, field, lang):
        """Find a row value given a field and language.

        An example of field and language might be "label" and "English".

        Args:
            field (str): The field from the header row.
            lang (str): The language.

        Returns:
            str: The value found from this row.
        """
        value = None
        try:
            if lang:
                if "{}::{}".format(field, lang) in self.row:
                    key = "{}::{}".format(field, lang)
                else:
                    key = "{}:{}".format(field, lang)
                value = self.row[key]
            else:
                keys = (k for k in self.row if k.startswith(field))
                first = sorted(keys)[0]
                value = self.row[first]
        except (KeyError, IndexError):
            # KeyError: self.row does not have the key '{}::/:{}'.
            # IndexError: `keys` (filtered by field) is empty list.
            pass
        return value

    def to_text_relevant(self, lang):
        """Get the relevant text for this prompt.

        Args:
            :param lang: (str) The language.

        Returns:
            str: The text representation of the relevant.
        """
        formatted_relevant = None
        relevant_text = self.text_field("relevant_text", lang)
        if relevant_text:
            # formatted_relevant = '[{}]'.format(relevant_text).rjust(50)
            formatted_relevant = "{}".format(relevant_text).rjust(50)
        return formatted_relevant

    def to_dict(self, lang, **kwargs):
        """Get the text representation of the detailed prompt.

        Args:
            lang (str): The language.
            **bottom_border (bool): Renders a border at bottom of prompt. This
                is necessary for section headers followed by a group.

        Returns:
            dict: The text from all parts of the prompt.
        """
        prompt = self._set_descriptive_metadata(self.row)
        prompt = self._reformat_default_lang_vars(prompt, lang)
        prompt = self._truncate_fields(prompt)
        prompt = self._reformat_double_line_breaks(prompt)

        if self.is_section_header:
            prompt["is_section_header"] = True
        if "bottom_border" in kwargs:
            prompt["bottom_border"] = True
        if "template" in kwargs:
            prompt = self.handle_template_presets(prompt, lang, kwargs["template"])
        return prompt

    @staticmethod
    def html_options(lang, **kwargs):
        """HTML options.

        Args:
            lang (str): The language.
            **kwargs (dict): Keyword arguments.

        Returns:
            dict: Modified settings based on keyword arguments.
        """
        if "template" not in kwargs:
            return kwargs
        for k, v in TEMPLATES[kwargs["template"]]["render_settings"]["html"].items():
            kwargs[k] = v
        if "language" not in kwargs:
            # noinspection PyTypeChecker
            kwargs["language"] = lang
        return kwargs

    def to_html(self, lang, **kwargs):
        """Convert to html.

        Args:
            lang (str): The language.
            **kwargs: Arbitrary keyword arguments delegated detailedy to
            to_dict().

        Returns:
            str: A rendered html template.
        """
        settings = self.html_options(lang=lang, **kwargs)
        question = self.to_dict(lang=lang, **settings)
        # pylint: disable=no-member
        return TEMPLATE_ENV.get_template("content/content-tr-base.html").render(
            question=question, **settings
        )
