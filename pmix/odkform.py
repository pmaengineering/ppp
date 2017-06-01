import os.path
import datetime
from pmix.ppp_config import template_env
from pmix.error import OdkformError
from pmix.odkchoices import OdkChoices
from pmix.odkgroup import OdkGroup
from pmix.odkprompt import OdkPrompt
from pmix.odkrepeat import OdkRepeat
from pmix.workbook import Workbook


class OdkForm:
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
        conversion_start = datetime.datetime.now()
        self.metadata = {  # TODO Finish filling this out.
            'file_name': os.path.split(wb.file)[1],
            'form_id': self.settings.get('form_id'),
            'country': self.settings.get('form_id')[3:5],
            'round': self.settings.get('form_id')[6:7],
            'type_of_form': self.settings.get('form_id')[0:2],
            'last_author': None,
            'last_updated': None,
            'conversion_start': conversion_start,
            'conversion_start_formatted': str(conversion_start.date()) + ' ' + str(conversion_start.time())[0:8],
            'conversion_end': None,
            'conversion_end_formatted': None,
            'conversion_time': None,
            'changelog': None,
            'info': None
        }
        self.conversion_settings = {
            'json_output_in_js_console': None,
            'highlighting': None
        }
        self.unhandled_token_types = ['calculate', 'start', 'end', 'deviceid', 'simserial', 'phonenumber', 'hidden',
                                      'hidden string', 'hidden int', 'hidden geopoint']
        self.warnings = None
        self.conversion_info = None
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
                    odkchoices = OdkChoices(list_name)
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

    def set_conversion_end(self):
        self.metadata['conversion_end'] = datetime.datetime.now()
        self.metadata['conversion_end_formatted'] = str(self.metadata['conversion_end'].date()) + ' ' + \
            str(self.metadata['conversion_end'].time())[0:8]

    def get_running_conversion_time(self):
        self.metadata['conversion_time'] = str(self.metadata['conversion_end'] -
                                               self.metadata['conversion_start'])[5:10] + ' ' + 'seconds'

        return self.metadata['conversion_time']

    def to_text(self, lang):
        """Get the text representation of an entire XLSForm

        :param lang: The language
        :return: The full string of the XLSForm, ready to print or save
        """
        lang = lang if lang else self.survey_language
        title_lines = (
            '+{:-^50}+'.format(''),
            '|{:^50}|'.format(self.title),
            '+{:-^50}+'.format('')
        )
        title_box = '\n'.join(title_lines)

        q_text = (q.to_text(lang) for q in self.questionnaire)
        sep = '\n\n' + '=' * 52 + '\n\n'
        result = sep.join(q_text)
        return title_box + sep + result + sep

    def to_dict(self, lang):
        """Get the dictionary representation of an entire XLSForm.

        :param lang: The language.
        :return: A dictionary formatted questionnaire.
        """
        lang = lang if lang else self.survey_language
        html_questionnaire = {
            'title': self.title,
            'questions': []
        }
        for q in self.questionnaire:
            html_questionnaire['questions'].append(q.to_dict(lang))
        return html_questionnaire

    def to_json(self, lang, pretty=False):
        """Get the JSON representation of an entire XLSForm.

        :param lang: The language.
        :param pretty: Printing with whitespace for readability.
        :return: A JSON formatted questionnaire.
        """
        import json
        lang = lang if lang else self.survey_language
        if pretty:
            return json.dumps(self.to_dict(lang), indent=2)
        else:
            return json.dumps(self.to_dict(lang))

    def to_html(self, lang, highlighting, debugging):
        lang = lang if lang else self.survey_language
        html_questionnaire = ''
        data = {
            'header': {
                'title': self.title
            },
            'footer': {
                'data': self.to_json(lang, pretty=True) if debugging else 'false'
            },
            'questionnaire': self.questionnaire
        }
        header = template_env.get_template('header.html').render(data=data['header'])
        gs = template_env.get_template('content/group/group-spacing.html').render()
        html_questionnaire += header
        prev_item = None
        for index, q in enumerate(data['questionnaire']):
            if prev_item is not None and isinstance(q, OdkGroup):
                html_questionnaire += gs
            elif isinstance(prev_item, OdkGroup) and not isinstance(q, OdkGroup):
                html_questionnaire += gs
            if isinstance(q, OdkPrompt) and q.is_section_header and isinstance(data['questionnaire'][index+1], OdkGroup):
                html_questionnaire += q.to_html(lang, highlighting, bottom_border=True)
            else:
                html_questionnaire += q.to_html(lang, highlighting)
            prev_item = q
        self.set_conversion_end()
        warnings = self.warnings if self.warnings is not None else 'false'
        self.conversion_info = {} if self.conversion_info is 'false' else self.conversion_info
        self.get_running_conversion_time()
        footer = template_env.get_template('footer.html').render(info=self.conversion_info, warnings=warnings,
                                                        conversion_time=str(self.metadata['conversion_time']),
                                                        data=data['footer']['data'])
        html_questionnaire += footer
        return html_questionnaire

    def parse_type(self, row):
        """Describe with JSON the 'type' column of a row XLSForm

        :param row: (dict) A row as a dictionary
        :return: (dict) Info from parsing
        """
        row_type = row['type']
        if row_type in OdkPrompt.response_types + OdkPrompt.non_response_types:
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
                dict_row = {str(k): str(v) for k, v in zip(header, row)}
                token = self.parse_type(dict_row)

                if token['token_type'] == 'prompt':
                    dict_row['simple_type'] = token['simple_type']
                    if 'choice_list' in token:
                        choices = token['choice_list']
                    else:
                        choices = None
                    # TODO: Refactor next if/else and this_prompt declaration. Should only render group at 'end group'.
                    if stack:
                        # This is de-activated. Will need to add group/repeat render_prompt to get it to work.
                        # dict_row['in_group'] = True if any(isinstance(x, OdkGroup) for x in stack) else False
                        # dict_row['in_repeat'] = True if any(isinstance(x, OdkRepeat) for x in stack) else False
                        pass
                    this_prompt = OdkPrompt(dict_row, choices)
                    if stack:
                        stack[-1].add(this_prompt)
                    else:
                        result.append(this_prompt)
                    # This is temporarily de-activated. Will need to add group/repeat rendering to get it to work.
                    # result.append(this_prompt)
                # TODO: Refactor begin and end group handling.
                elif token['token_type'] == 'begin group':
                    if not stack or isinstance(stack[-1], OdkRepeat):
                        group = OdkGroup(dict_row)
                        stack.append(group)
                        # This is temporarily de-activated. Will need to add group/repeat rendering to get it to work.
                        # result.append(group.header)
                    else:
                        m = 'Unable to add group at row {}'.format(i + 1)
                        raise OdkformError(m)
                elif token['token_type'] == 'end group':
                    c = context_groups
                    if c and c[-1]['name'] == dict_row['name'] and c[-1]['is_closed'] is False:
                        c[-1]['is_closed'] = True
                    else:
                        if stack and isinstance(stack[-1], OdkGroup):
                            group = stack.pop()
                            group.add_pending()
                            if stack:
                                stack[-1].add(group)
                            else:
                                # - New rendering. Disable this if needed as errors occur.
                                result.append(group)
                                # pass
                            # This is temporarily de-activated. Will need to add group/repeat rendering to get it to
                            # work. end_group = OdkGroup(dict_row)  # This is a band-aid for replacement in refactoring.
                            # result.append(end_group.footer)
                        else:
                            m = 'Mismatched "end group" at row {}'.format(i + 1)
                            raise OdkformError(m)
                elif token['token_type'] == 'begin repeat':
                    if not stack:
                        repeat = OdkRepeat(dict_row)
                        stack.append(repeat)
                    else:
                        m = 'Unable to add repeat at row {}'.format(i + 1)
                        raise OdkformError(m)
                elif token['token_type'] == 'end repeat':
                    if stack and isinstance(stack[-1], OdkRepeat):
                        # This is temporarily de-activated. Will need to add group/repeat rendering to get it to work.
                        # stack.pop()  # Stack guaranteed empty at this point.
                        # TODO: Render repeat from here.
                        # - New rendering. Disable this if needed as errors occur.
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
                    if stack and isinstance(stack[-1], OdkGroup):
                        this_prompt = OdkPrompt(dict_row, choices)
                        stack[-1].add_table(this_prompt)
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
                    if stack and isinstance(stack[-1], OdkGroup):
                        m = ('PPP does not allow a group nested in a '
                             'field-list group. See row {}').format(i + 1)
                        raise OdkformError(m)
                elif token['token_type'] in self.unhandled_token_types:  # Intentionally no handling for these types.
                    self.conversion_info = {} if self.conversion_info is None else self.conversion_info
                    k = 'Unhandled Token Types'
                    if k not in self.conversion_info:
                        self.conversion_info[k] = []
                    if token['token_type'] not in self.conversion_info[k]:
                        self.conversion_info[k].append(token['token_type'])
                else:
                    self.warnings = {} if self.warnings is None else self.warnings
                    k = 'Unknown Token Types'
                    if k not in self.warnings:
                        self.warnings[k] = []
                    if token['token_type'] not in self.warnings[k]:
                        self.warnings[k].append(token['token_type'])
        except KeyError:  # No survey found.
            pass
        return result
