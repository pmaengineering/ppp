import os.path
import datetime
from jinja2 import Environment, PackageLoader
from pmix.error import OdkformError
from pmix.odkchoices import Odkchoices
from pmix.odkgroup import Odkgroup
from pmix.odkprompt import Odkprompt
from pmix.odkrepeat import Odkrepeat
from pmix.workbook import Workbook


class Odkform:
    """Class to represent an entire XLSForm"""

    def __init__(self, *, f=None, wb=None):
        if f is None and wb is None:
            raise OdkformError()
        elif f is not None:
            wb = Workbook(f)

        self.settings = self.get_settings(wb)
        self.title = self.settings.get('form_title', os.path.split(wb.file)[1])
        self.languages = self.get_languages(wb)
        self.survey_language = self.get_survey_language()
        self.choices = self.get_choices(wb, 'choices')
        self.external_choices = self.get_choices(wb, 'external_choices')
        self.metadata = {  # TODO Finish filling this out.
            'file_name': os.path.split(wb.file)[1],
            'form_id': self.settings.get('form_id'),
            'country': self.settings.get('form_id')[3:5],
            'round': self.settings.get('form_id')[6:7],
            'type_of_form': self.settings.get('form_id')[0:2],
            'last_author': '',
            'last_updated': '',
            'last_converted': str(datetime.datetime.now().date()) + ' ' + str(datetime.datetime.now().time())[0:8],
            'changelog': '',
            'info': ''
        }
        self.conversion_settings = {
            'json_output_in_js_console': True
        }
        self.unhandled_token_types = ['calculate', 'start', 'end', 'deviceid', 'simserial', 'phonenumber',
                                      'hidden string', 'hidden int', 'hidden geopoint']
        self.warnings = {}
        self.conversion_info = {}
        self.questionnaire = self.convert_survey(wb)

    @staticmethod
    def get_settings(wb):
        """Get the XLSForm settings as a dict

        :param wb: Source workbook
        :return: (dict) Form settings
        """
        d = {}
        try:
            settings = wb['settings']
            header = settings[0]
            details = settings[1]
            d = {k: v for k, v in zip(header, details)}
        except (KeyError, IndexError):
            # KeyError: worksheet does not exist
            # IndexError: does not have the correct rows
            pass
        return d

    @staticmethod
    def get_choices(wb, ws):
        """Extract choices from an XLSForm

        :param wb: Source workbook
        :param ws: One of 'choices' or 'external_choices'
        :return: Dict with keys as list names
        """
        d = {}
        try:
            choices = wb[ws]
            header = choices[0]
            if 'list_name' not in header:
                m = 'Column "list_name" not found in {} tab'.format(ws)
                raise OdkformError(m)
            for i, row in enumerate(choices):
                if i == 0:
                    continue
                json_row = {k: v for k, v in zip(header, row)}
                list_name = json_row['list_name']
                if list_name in d:
                    d[list_name].add(json_row)
                elif list_name:  # Not "else:" because possibly blank rows.
                    odkchoices = Odkchoices(list_name)
                    odkchoices.add(json_row)
                    d[list_name] = odkchoices
        except KeyError:  # Worksheet does not exist.
            pass
        return d

    @staticmethod
    def get_languages(wb):
        header = wb['survey'][0]
        langs = set()
        for field in header:
            # TODO: Handle the following cases, both with cases of a presence of 'default_language', and not.
            # 1. No 'label' or 'label::' fields at all, 2. A 'label' field by itself.
            # 3. A 'label' field with 'label::' fields.
            if field == 'label':
                langs.add('')  # Default language.
            elif field.startswith('label::'):
                lang = field[len('label::'):]
                langs.add(lang)
        return sorted(list(langs))

    def get_survey_language(self):
        return self.settings['default_language'] if 'default_language' in self.settings else self.languages[0]

    def to_text(self, lang=None):
        """Get the text representation of an entire XLSForm

        :param lang: The language
        :return: The full string of the XLSForm, ready to print or save
        """
        title_lines = (
            '+{:-^50}+'.format(''),
            '|{:^50}|'.format(self.title),
            '+{:-^50}+'.format('')
        )
        title_box = '\n'.join(title_lines)

        q_text = (q.to_text(lang=lang) for q in self.questionnaire)
        sep = '\n\n' + '=' * 52 + '\n\n'
        result = sep.join(q_text)
        return title_box + sep + result + sep

    def to_dict(self, lang=None):
        """Get the dictionary representation of an entire XLSForm.

        :param lang: The language.
        :return: A dictionary formatted questionnaire.
        """
        html_questionnaire = {
            'title': self.title,
            'questions': []
        }
        for q in self.questionnaire:
            html_questionnaire['questions'].append(q.to_dict(lang=lang))
        return html_questionnaire

    def to_json(self, lang=None, pretty=False):
        """Get the JSON representation of an entire XLSForm.

        :param lang: The language.
        :param pretty: Printing with whitespace for readability.
        :return: A JSON formatted questionnaire.
        """
        import json
        if pretty:
            return json.dumps(self.to_dict(lang), indent=2)
        else:
            return json.dumps(self.to_dict(lang))

    def to_html(self, lang=None):
        env = Environment(loader=PackageLoader('pmix'))
        html_questionnaire = ''
        data = {
            'header': {
                'title': self.title
            },
            'footer': {
                'data': ''
            },
            'questionnaire': self.questionnaire
        }
        if self.conversion_settings['json_output_in_js_console']:
            data['footer']['data'] = self.to_json(lang, pretty=True)
        header = env.get_template('header.html').render(data=data['header'])
        html_questionnaire += header
        for q in data['questionnaire']:
            html_questionnaire += q.to_html(lang=lang)
        footer = env.get_template('footer.html').render(info=self.conversion_info, warnings=self.warnings,
                                                        data=data['footer']['data'])
        html_questionnaire += footer
        return html_questionnaire

    def parse_type(self, row):
        """Describe with JSON the 'type' column of a row XLSForm

        :param row: (dict) A row as a dictionary
        :return: (dict) Info from parsing
        """
        row_type = row['type']
        if row_type in Odkprompt.response_types + Odkprompt.non_response_types:
            d = {
                'token_type': 'prompt',
                'simple_type': row_type
            }
            return d
        elif row_type.startswith('select_one_external '):
            choice_list = row_type.split(maxsplit=1)[1]
            choices = self.external_choices[choice_list]
            return {
                'token_type': 'prompt',
                'simple_type': 'select_one',
                'choice_list': choices
            }
        elif row_type.startswith('select_multiple_external '):
            choice_list = row_type.split(maxsplit=1)[1]
            choices = self.external_choices[choice_list]
            return {
                'token_type': 'prompt',
                'simple_type': 'select_multiple',
                'choice_list': choices
            }
        elif row_type.startswith('select_one '):
            choice_list = row_type.split(maxsplit=1)[1]
            choices = self.choices[choice_list]
            d = {
                'token_type': 'prompt',
                'simple_type': 'select_one',
                'choice_list': choices
            }
            table_label = 'label' in row.get('appearance', '')
            table_list = 'list-nolabel' in row.get('appearance', '')
            if table_label or table_list:
                d['token_type'] = 'table'
            return d
        elif row_type.startswith('select_multiple '):
            choice_list = row_type.split(maxsplit=1)[1]
            choices = self.choices[choice_list]
            d = {
                'token_type': 'prompt',
                'simple_type': 'select_multiple',
                'choice_list': choices
            }
            table_label = 'label' in row.get('appearance', '')
            # - Note: list-nolabel is like a table within a table. Whereas the field-list on its own is a table
            # comprised primarily of rows, list-nolabel is comprised primarily of columns and a header.
            table_list = 'list-nolabel' in row.get('appearance', '')
            if table_label or table_list:
                d['token_type'] = 'table'
            return d
        # TODO: Work below this line as necessary to handle groups, repeats, and tables correctly.
        elif row_type == 'begin group':
            d = {'token_type': 'context group'}
            appearance = row.get('appearance', '')
            if 'field-list' in appearance:
                # - Note: This returns "begin group" which will render visually since it is a 'field-list', and not just
                #  a group that is there solely for context.
                d['token_type'] = row_type
            return d
        elif row_type in ('end group', 'begin repeat', 'end repeat'):
            return {
                'token_type': row_type
            }
        else:  # Note - Some unhandled token types remain.
            return{'token_type': row_type}

    def convert_survey(self, wb):
        """Convert rows and strings of a workbook into better python objects

        Main types are

        - prompt
        - begin group
        - end group
        - begin repeat
        - end repeat
        - table
        - context group (group without field-list appearance)

        :param wb: Workbook object representing an XLSForm.
        :return: A list of better python objects
        """
        result = []
        stack = []
        context_groups = []
        try:
            survey = wb['survey']
            header = survey[0]

            for i, row in enumerate(survey):
                if i == 0:
                    continue
                dict_row = {k: v for k, v in zip(header, row)}
                token = self.parse_type(dict_row)

                if token['token_type'] == 'prompt':
                    dict_row['simple_type'] = token['simple_type']
                    if 'choice_list' in token:
                        choices = token['choice_list']
                    else:
                        choices = None
                    if stack:
                        dict_row['in_group'] = True
                    else:
                        dict_row['in_group'] = False
                    this_prompt = Odkprompt(dict_row, choices)
                    if stack:
                        stack[-1].add(this_prompt)
                    result.append(this_prompt)
                elif token['token_type'] == 'begin group':
                    if not stack or isinstance(stack[-1], Odkrepeat):
                        group = Odkgroup(dict_row, )
                        stack.append(group)
                        result.append(group.header)
                    else:
                        m = 'Unable to add group at row {}'.format(i + 1)
                        raise OdkformError(m)
                elif token['token_type'] == 'end group':
                    c = context_groups
                    if c and c[-1]['name'] == dict_row['name'] and c[-1]['is_closed'] is False:
                        c[-1]['is_closed'] = True
                    else:
                        if stack and isinstance(stack[-1], Odkgroup):
                            group = stack.pop()
                            group.add_pending()
                            if stack:
                                stack[-1].add(group)
                            else:
                                result.append(group.footer)
                        else:
                            m = 'Mismatched "end group" at row {}'.format(i + 1)
                            raise OdkformError(m)
                elif token['token_type'] == 'begin repeat':
                    if not stack:
                        repeat = Odkrepeat(dict_row, )
                        stack.append(repeat)
                    else:
                        m = 'Unable to add repeat at row {}'.format(i + 1)
                        raise OdkformError(m)
                elif token['token_type'] == 'end repeat':
                    if stack and isinstance(stack[-1], Odkrepeat):
                        repeat = stack.pop()  # Stack guaranteed empty at this point.
                        result.append(repeat)
                    else:
                        m = 'Mismatched "end repeat" at row {}'.format(i + 1)
                        raise OdkformError(m)
                elif token['token_type'] == 'table':
                    dict_row['simple_type'] = token['simple_type']
                    if 'choice_list' in token:
                        choices = token['choice_list']
                    else:
                        choices = None
                    if stack and isinstance(stack[-1], Odkgroup):
                        this_prompt = Odkprompt(dict_row, choices)
                        stack[-1].add_table(this_prompt)
                        result.append(this_prompt)
                    else:
                        m = 'Table found outside of field-list group at row {}'
                        m = m.format(i + 1)
                        raise OdkformError(m)
                elif token['token_type'] == 'context group':
                    if any(d['name'] == dict_row['name'] for d in context_groups):
                        m = 'A context group with this name already exists in survey.'
                        raise OdkformError(m)
                    else:
                        this_context_group = {
                            'name': dict_row['name'],
                            'is_closed': False,
                            'data': dict_row
                        }
                        context_groups.append(this_context_group)
                    if stack and isinstance(stack[-1], Odkgroup):
                        m = ('PPP does not allow a group nested in a '
                             'field-list group. See row {}').format(i + 1)
                        raise OdkformError(m)
                elif token['token_type'] in self.unhandled_token_types:  # Intentionally no handling for these types.
                    k = 'Unhandled Token Types'
                    if k not in self.conversion_info:
                        self.conversion_info[k] = []
                    else:
                        if token['token_type'] not in self.conversion_info[k]:
                            self.conversion_info[k].append(token['token_type'])
                else:
                    k = 'Unknown Token Types'
                    if k not in self.warnings:
                        self.warnings[k] = []
                    else:
                        if token['token_type'] not in self.warnings[k]:
                            self.warnings[k].append(token['token_type'])
        except KeyError:  # No survey found.
            pass
        return result
