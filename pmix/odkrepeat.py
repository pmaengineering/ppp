from jinja2 import Environment, PackageLoader
import textwrap
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

    def to_dict(self, lang):
        """Get the text representation of the entire repeat group

        :param lang: (str) The language.
        :return: (dict) The text for this repeat.
        """
        pass

    # def to_html(self, lang, highlighting):
    #     env = Environment(loader=PackageLoader('pmix'))
    #     question = env.get_template('content/content-tr-base.html').render(question=self.to_dict(lang=lang),
    #                                                                        highlighting=highlighting)
    #     return question

    def render_header(self, input, lang, highlighting):
        env = Environment(loader=PackageLoader('pmix'))
        s = env.get_template('content/repeat-opener.html').render()
        input['simple_type'] = input['type']
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
        env = Environment(loader=PackageLoader('pmix'))
        return env.get_template('content/repeat-closer.html').render()

    def render_prompt(self, input, lang, highlighting):
        # input.row['in_repeat'] = True
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
        print(self.data)  # DEBUG
        s = ''  # TODO: Below this line.
        s += self.render_header(self.opener, lang, highlighting)
        # if isinstance(self.data[-1], OdkTable) is True:
        #     self.data[-1].is_repeat_footer = True
        # for i in self.data[0:-1]:
        for i in self.data:
            if isinstance(i, OdkPrompt):
                s += (self.render_prompt(i, lang, highlighting))
            elif isinstance(i, OdkGroup):
                i.to_html(lang, highlighting)
            elif isinstance(i, OdkTable):
                i.to_html(lang, highlighting)
        s += self.render_footer()
        # s += self.render_footer(self.data[-1], lang, highlighting) if isinstance(self.data[-1], OdkPrompt) else \
        #     self.data[-1].to_html(lang, highlighting) if isinstance(self.data[-1], OdkTable) else ''
        return s
