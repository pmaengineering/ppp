import os.path

from pmix.error import OdkformError
from pmix.odkchoices import Odkchoices
from pmix.odkprompt import Odkprompt
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

        :param wb: Workbook object representing an XLSForm.
        :return: A list of better python objects
        """
        result = []
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
                    result.append(this_prompt)
                # TODO Check for begin group/repeat, end group/repeat, table
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
            return {
                'token_type': 'prompt',
                'simple_type': row_type
            }
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
            return {
                'token_type': 'prompt',
                'simple_type': 'select_one',
                'choice_list': choices
            }
        elif row_type.startswith('select_multiple '):
            choice_list = row_type.split(maxsplit=1)[1]
            choices = self.choices[choice_list]
            return {
                'token_type': 'prompt',
                'simple_type': 'select_multiple',
                'choice_list': choices
            }
        # TODO add in support for "begin group", "end group", "begin repeat",
        # TODO "end repeat", and "table" here
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
