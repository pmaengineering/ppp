import os.path

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
        self.choices = self.get_choices(wb, 'choices')
        self.external_choices = self.get_choices(wb, 'external_choices')
        self.questionnaire = self.convert_survey(wb)

        self.title = self.settings.get('form_title', os.path.split(wb.file)[1])

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
        try:
            survey = wb['survey']
            header = survey[0]
            for i, row in enumerate(survey):
                if i == 0:
                    continue
                json_row = {k: v for k, v in zip(header, row)}
                token = self.parse_type(json_row)
                if token['token_type'] == 'prompt':
                    json_row['simple_type'] = token['simple_type']
                    if 'choice_list' in token:
                        choices = token['choice_list']
                    else:
                        choices = None
                    this_prompt = Odkprompt(json_row, choices)
                    if stack:
                        stack[-1].add(this_prompt)
                    else:
                        result.append(this_prompt)
                elif token['token_type'] == 'begin group':
                    if not stack or isinstance(stack[-1], Odkrepeat):
                        group = Odkgroup(json_row)
                        stack.append(group)
                    else:
                        m = 'Unable to add group at row {}'.format(i+1)
                        raise OdkformError(m)
                elif token['token_type'] == 'end group':
                    if stack and isinstance(stack[-1], Odkgroup):
                        group = stack.pop()
                        group.add_pending()
                        if stack:
                            stack[-1].add(group)
                        else:
                            result.append(group)
                    else:
                        m = 'Mismatched "end group" at row {}'.format(i+1)
                        raise OdkformError(m)
                elif token['token_type'] == 'begin repeat':
                    if not stack:
                        repeat = Odkrepeat(json_row)
                        stack.append(repeat)
                    else:
                        m = 'Unable to add repeat at row {}'.format(i+1)
                        raise OdkformError(m)
                elif token['token_type'] == 'end repeat':
                    if stack and isinstance(stack[-1], Odkrepeat):
                        repeat = stack.pop()
                        # Stack guaranteed empty at this point
                        result.append(repeat)
                    else:
                        m = 'Mismatched "end repeat" at row {}'.format(i+1)
                        raise OdkformError(m)
                elif token['token_type'] == 'table':
                    if stack and isinstance(stack[-1], Odkgroup):
                        stack[-1].add_table(json_row)
                    else:
                        m = 'Table found outside of field-list group at row {}'
                        m = m.format(i+1)
                        raise OdkformError(m)
                elif token['token_type'] == 'context group':
                    if stack and isinstance(stack[-1], Odkgroup):
                        m = ('PPP does not allow a group nested in a '
                             'field-list group. See row {}').format(i+1)
                        raise OdkformError(m)
        except KeyError:
            # no survey found
            pass
        return result

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
            table_list = 'list-nolabel' in row.get('appearance', '')
            if table_label or table_list:
                d['token_type'] = 'table'
            return d
        elif row_type == 'begin group':
            d = {'token_type': 'context group'}
            appearance = row.get('appearance', '')
            if 'field-list' in appearance:
                d['token_type'] = row_type
            return d
        elif row_type in ('end group', 'begin repeat', 'end repeat'):
            return {
                'token_type': row_type
            }
        else:
            return {'token_type': None}

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
                elif list_name: # not "else:" because possibly blank rows
                    odkchoices = Odkchoices(list_name)
                    odkchoices.add(json_row)
                    d[list_name] = odkchoices
        except KeyError:
            # worksheet does not exist
            pass
        return d
