import textwrap
from pmix.ppp_config import template_env
from pmix.odkprompt import OdkPrompt
from pmix.odkgroup import OdkGroup
from pmix.odktable import OdkTable

class OdkRepeat:
    """Class to represent repeat construct from XLSForm"""

    def __init__(self, opener):
        """Initialize repeat object with empty data bin"""
        self.opener = opener
        self.data = []

    def __repr__(self):
        s = "<OdkRepeat {}: {}>".format(self.opener['name'], self.data)
        return s

    def add(self, obj):
        """Add XLSForm object to repeat

        Only other prompts and groups are allowed to be added.

        :param obj: either Odkgroup or Odkprompt
        """
        self.data.append(obj)

    def to_text(self, lang):
        """Get the text representation of the entire repeat group

        :param lang: (str) The language
        :return: (str) The text for this repeat
        """
        obj_texts = (d.to_text(lang) for d in self.data)
        sep = '\n\n{}\n\n'.format('=' * 50)
        repeat_text = sep.join(obj_texts)
        wrapped = textwrap.indent(repeat_text, '|  ', lambda x: True)
        return wrapped

    def render_header(self, input, lang, highlighting):

        s = template_env.get_template('content/repeat/repeat-opener.html').render()
        input['simple_type'] = input['type']
        input['in_repeat'] = True
        input['is_repeat_header'] = True
        s += OdkPrompt(input).to_html(lang, highlighting)
        return s
        # s = ''
        # s += '<table style="background: blue;"><tr><td>'
        # input['simple_type'] = input['type']
        # input['is_repeat_header'] = True
        # s += OdkPrompt(input).to_html(lang, highlighting)
        # return s

    def render_footer(self):
    # def render_footer(self, input, lang, highlighting):
        # input.row['in_repeat'] = True
        # input.row['is_repeat_footer'] = True
        # return input.to_html(lang, highlighting)

        return template_env.get_template('content/repeat/repeat-closer.html').render()

    def render_prompt(self, input, lang, highlighting):
        input.row['in_repeat'] = True
        return input.to_html(lang, highlighting)

    # def render_group(self, input, lang, highlighting):
    #     pass
    #
    # def render_table(self, input, lang, highlighting):
    #     pass

    def to_html(self, lang, highlighting):
        """Get the html representation of the full group.

        :param lang: (str) The language.
        :param highlighting: (bool) Highlighting on/off.
        :return: (dict) The text for this group.
        """
        s = ''
        s += self.render_header(self.opener, lang, highlighting)
        for i in self.data:
            if isinstance(i, OdkPrompt):
                i.row['in_repeat'] = True
                s += i.to_html(lang, highlighting)
            elif isinstance(i, OdkGroup):
                i.in_repeat = True
                s += i.to_html(lang, highlighting)
            elif isinstance(i, OdkTable):
                i.in_repeat = True
                s += i.to_html(lang, highlighting)
        s += self.render_footer()
        return s
