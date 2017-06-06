"""Module for the OdkForm class."""
import datetime
import os.path
from pmix.ppp.config import TEMPLATE_ENV
from pmix.ppp.odkchoices import OdkChoices
from pmix.ppp.odkgroup import OdkGroup
from pmix.ppp.odkprompt import OdkPrompt
from pmix.ppp.error import OdkFormError
from pmix.ppp.odkrepeat import OdkRepeat
from pmix.workbook import Workbook


class OdkForm:
    """Class to represent an entire XLSForm.

    Attributes:
        settings (dict): A dictionary represetnation of the original 'settings'
            worksheet of an ODK XLSForm.
        title (str): Title of the ODK form.
        languages (list): List of languages used in the ODK form. This is taken
            from the 'survey' worksheet.
        choices (list): A list of rows from the 'choices' worksheet.
        external_choices (list): A list of rows from the 'external_choices'
            worksheet.
        metadata (dict): A dictionary of metadata for the original and
            converted ODK forms.
        questionnaire (list): An ordered representation of the ODK form,
            comprised of OdkPrompt, OdkGroup, OdkRepeat, and OdkTable objects.
    """

    def __init__(self, file=None, wb=None):
        """Initialize the OdkForm.

        Create an instance of an ODK form, including survey representation,
        choice options, settings, and metadata.

        Args:
            file (str): The path for the source file of the ODK form,
                typically an '.xlsx' file meeting the XLSForm specification.
            wb (Workbook): A Workbook object meeting XLSForm specification.
        Raises:
            OdkformError: No ODK form is supplied.
            InvalidLanguage: Language specified is not found in form.
        """
        if file is None and wb is None:
            raise OdkFormError()
        elif file is not None:
            wb = Workbook(file)

        self.settings = {str(k): str(v) for k, v in
                         self.get_settings(wb).items()}
        self.title = self.settings.get('form_title', os.path.split(wb.file)[1])
        self.languages = self.get_languages(wb)
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
            'survey_language': self.get_survey_language(),
            'conversion_start': conversion_start,
            'conversion_start_formatted':
                str(conversion_start.date()) +
                ' ' + str(conversion_start.time())[0:8],
            'conversion_end': None,
            'conversion_end_formatted': None,
            'conversion_time': None,
            'changelog': None,
            'info': None
        }
        self.questionnaire = self.convert_survey(wb)

    unhandled_token_types = \
        ['calculate', 'start', 'end', 'deviceid', 'simserial',
         'phonenumber', 'hidden', 'hidden string', 'hidden int',
         'hidden geopoint']
    warnings = None
    conversion_info = None

    @staticmethod
    def get_settings(wb):
        """Get the XLSForm settings as a settings_dict.

        Args:
            wb (Workbook): A workbook object representing ODK form.

        Returns:
            dict: Form settings.:
        """
        settings_dict = {}
        try:
            settings = wb['settings']
            header = settings[0]
            details = settings[1]
            settings_dict = {k: v for k, v in zip(header, details)}
        except (KeyError, IndexError):
            # KeyError: Worksheet does not exist.
            # IndexError: Does not have the correct rows.
            pass
        return settings_dict

    @staticmethod
    def get_choices(wb, ws):
        """Extract choices from an XLSForm.

        Args:
            wb (Workbook): A Workbook object representing ODK form.
            ws (Worksheet): One of 'choices' or 'external_choices'.

        Returns:
            dict: A dictionary of choice list names with list of choices
                options for each list.

        Raises:
            OdkformError: Catches instances where list specified in the
                'survey' worksheet, but the list does not appear in the
                designated 'choices' or 'external_choices' worksheet.
        """
        formatted_choices = {}
        try:
            choices = wb[ws]
            header = [str(x) for x in choices[0]]
            if 'list_name' not in header:
                msg = 'Column "list_name" not found in {} tab'.format(ws)
                raise OdkFormError(msg)
            for i, row in enumerate(choices):
                if i == 0:
                    continue
                dict_row = {str(k): str(v) for k, v in zip(header, row)}
                list_name = dict_row['list_name']
                if list_name in formatted_choices:
                    formatted_choices[list_name].add(dict_row)
                elif list_name:  # Not "else:" because possibly blank rows.
                    odkchoices = OdkChoices(list_name)
                    odkchoices.add(dict_row)
                    formatted_choices[list_name] = odkchoices
        except KeyError:  # Worksheet does not exist.
            pass
        return formatted_choices

    @staticmethod
    def get_languages(wb):
        """Get survey languages.

        Args:
            wb (Workbook): A Workbook object representing ODK form.

        Returns:
            list: An alphabetically sorted list of languages in the form.
        """
        header = wb['survey'][0]
        langs = set()
        for field in header:
            # TODO: Handle the following cases, both with cases of a presence
            # of 'default_language', and not.
            # 1. No 'label' or 'label::' fields at all,
            # 2. A 'label' field by itself.
            # 3. A 'label' field with 'label::' fields.
            if field == 'label':
                langs.add('')  # Default language.
            elif str(field).startswith('label::'):
                lang = str(field)[len('label::'):]
                langs.add(lang)
        return sorted(list(langs))

    def get_survey_language(self):
        """Get default survey language if specified.

        Returns:
            str: The default language of the form.
        """
        return self.settings['default_language'] \
            if 'default_language' in self.settings else self.languages[0]

    def set_conversion_end(self):
        """Set conversion end time."""
        self.metadata['conversion_end'] = datetime.datetime.now()
        self.metadata['conversion_end_formatted'] = \
            str(self.metadata['conversion_end'].date()) + ' ' + \
            str(self.metadata['conversion_end'].time())[0:8]

    def get_running_conversion_time(self):
        """Get running conversion time at this point in time.

        Returns:
            str: Total time taken to convert form.
        """
        self.metadata['conversion_time'] = \
            str(self.metadata['conversion_end'] - self.metadata[
                'conversion_start'])[5:10] + ' ' + 'seconds'

        return self.metadata['conversion_time']

    def to_text(self, lang):
        """Get the text representation of an entire XLSForm.

        Args:
            lang (str): The language.

        Returns:
            str: The full string of the XLSForm, ready to print or save.
        """
        lang = lang if lang else self.metadata['survey_language']
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

        Args:
            lang (str): The language.

        Returns:
            dict: A full dictionary representation of the XLSForm.
        """
        lang = lang if lang else self.metadata['survey_language']
        html_questionnaire = {
            'title': self.title,
            'questions': []
        }
        for item in self.questionnaire:
            html_questionnaire['questions'].append(item.to_dict(lang))
        return html_questionnaire

    def to_json(self, lang, pretty=False):
        """Get the JSON representation of an entire XLSForm.

        Args:
            lang (str): The language.
            pretty (bool): Activates prettification, involving insertion of
                several kinds of whitespace for readability.

        Returns:
            json: A full JSON representation of the XLSForm.
        """
        import json
        lang = lang if lang else self.metadata['survey_language']
        if pretty:
            return json.dumps(self.to_dict(lang), indent=2)
        else:
            return json.dumps(self.to_dict(lang))

    def to_html(self, lang, highlighting, debugging):
        """Get the JSON representation of an entire XLSForm.

        Args:
            lang (str): The language.
            highlighting (bool): For color highlighting of various components
                of html template.
            debugging (bool): For inclusion of debug information to be printed
                in the JavaScript console.

        Returns:
            str: A full HTML representation of the XLSForm.
        """
        lang = lang if lang else self.metadata['survey_language']
        html_questionnaire = ''
        data = {
            'header': {
                'title': self.title
            },
            'footer': {
                'data':
                    self.to_json(lang, pretty=True) if debugging else 'false'
            },
            'questionnaire': self.questionnaire
        }
        # pylint: disable=no-member
        header = TEMPLATE_ENV.get_template('header.html')\
            .render(data=data['header'])
        # pylint: disable=no-member
        grp_spc = TEMPLATE_ENV\
            .get_template('content/group/group-spacing.html').render()
        html_questionnaire += header
        prev_item = None
        for index, item in enumerate(data['questionnaire']):
            if prev_item is not None and isinstance(item, OdkGroup):
                html_questionnaire += grp_spc
            elif isinstance(prev_item, OdkGroup) \
                    and not isinstance(item, OdkGroup):
                html_questionnaire += grp_spc
            if isinstance(item, OdkPrompt) and item.is_section_header and \
                    isinstance(data['questionnaire'][index+1], OdkGroup):
                html_questionnaire += item.to_html(lang, highlighting,
                                                   bottom_border=True)
            else:
                html_questionnaire += item.to_html(lang, highlighting)
            prev_item = item
        self.set_conversion_end()
        OdkForm.warnings = OdkForm.warnings if OdkForm.warnings is not None \
            else 'false'
        OdkForm.conversion_info = {} if OdkForm.conversion_info is 'false' \
            else OdkForm.conversion_info
        self.get_running_conversion_time()
        # pylint: disable=no-member
        footer = TEMPLATE_ENV.get_template('footer.html')\
            .render(info=OdkForm.conversion_info, warnings=OdkForm.warnings,
                    conversion_time=str(self.metadata['conversion_time']),
                    data=data['footer']['data'])
        html_questionnaire += footer
        return html_questionnaire

    def parse_type(self, row):
        """Describe the 'type' column of a row XLSForm.

        Args:
            row (dict): A row as a dictionary.

        Returns:
            dict: row_type information from parsing.
        """
        original_row_type = row['type']
        if original_row_type in OdkPrompt.response_types + \
                OdkPrompt.non_response_types:
            row_type = {
                'token_type': 'prompt',
                'simple_type': original_row_type
            }
        elif original_row_type.startswith('select_one_external '):
            choice_list = original_row_type.split(maxsplit=1)[1]
            choices = self.external_choices[choice_list]
            row_type = {
                'token_type': 'prompt',
                'simple_type': 'select_one',
                'choice_list': choices
            }
        elif original_row_type.startswith('select_multiple_external '):
            choice_list = original_row_type.split(maxsplit=1)[1]
            choices = self.external_choices[choice_list]
            row_type = {
                'token_type': 'prompt',
                'simple_type': 'select_multiple',
                'choice_list': choices
            }
        elif original_row_type.startswith('select_one '):
            choice_list = original_row_type.split(maxsplit=1)[1]
            choices = self.choices[choice_list]  # Breaks on this line. nothing
            #  seems to happen after.
            row_type = {
                'token_type': 'prompt',
                'simple_type': 'select_one',
                'choice_list': choices
            }
            table_label = 'label' in row.get('appearance', '')
            table_list = 'list-nolabel' in row.get('appearance', '')
            if table_label or table_list:
                row_type['token_type'] = 'table'
            return row_type
        elif original_row_type.startswith('select_multiple '):
            choice_list = original_row_type.split(maxsplit=1)[1]
            choices = self.choices[choice_list]
            row_type = {
                'token_type': 'prompt',
                'simple_type': 'select_multiple',
                'choice_list': choices
            }
            table_label = 'label' in row.get('appearance', '')
            # - Note: list-nolabel is like a table within a table. Whereas the
            # field-list on its own is a table
            # comprised primarily of rows, list-nolabel is comprised primarily
            # of columns and a header.
            table_list = 'list-nolabel' in row.get('appearance', '')
            if table_label or table_list:
                row_type['token_type'] = 'table'
            return row_type
        elif original_row_type == 'begin group':
            row_type = {'token_type': 'context group'}
            appearance = row.get('appearance', '')
            if 'field-list' in appearance:
                # - Note: This returns "begin group" which will render visually
                #  since it is a 'field-list', and not just
                #  a group that is there solely for context.
                row_type['token_type'] = original_row_type
            return row_type
        elif original_row_type in ('end group', 'begin repeat', 'end repeat'):
            row_type = {
                'token_type': original_row_type
            }
        else:  # Note - Some unhandled token types remain.
            row_type = {'token_type': original_row_type}
        return row_type

    # TODO: Resolve the following 4 pylint violations:
    #  1. too-many-branches
    #  2. too-many-nested-blocks
    #  3. too-many-statements
    #  4. too-many-locals
    def convert_survey(self, wb):
        """Convert rows and strings of a workbook into object components.

        Main types are:

        - prompt
        - begin group
        - end group
        - begin repeat
        - end repeat
        - table
        - context group (group without field-list appearance)

        Args:
            wb (Workbook): A Workbook object representing an XLSForm.

        Returns:
            list: A list of objects representing form components.

        Raises:
            OdkformError: Handle several errors, including: mismatched groups
                or repeat groups, errors when appending to groups or repeat
                groups, erroneously formed tables, duplicate context group
                names, and groups nested within a field-list group.
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
                    this_prompt = OdkPrompt(dict_row, choices)
                    if stack:
                        stack[-1].add(this_prompt)
                    else:
                        result.append(this_prompt)
                elif token['token_type'] == 'begin group':
                    if not stack or isinstance(stack[-1], OdkRepeat):
                        group = OdkGroup(dict_row)
                        stack.append(group)
                    else:
                        msg = 'Unable to add group at row {}'.format(i + 1)
                        raise OdkFormError(msg)
                elif token['token_type'] == 'end group':
                    if context_groups and context_groups[-1]['name'] == \
                            dict_row['name'] \
                            and context_groups[-1]['is_closed'] is False:
                        context_groups[-1]['is_closed'] = True
                    else:
                        if stack and isinstance(stack[-1], OdkGroup):
                            group = stack.pop()
                            group.add_pending()
                            if stack:
                                stack[-1].add(group)
                            else:
                                result.append(group)
                        else:
                            msg = 'Mismatched "end group" at row {}'\
                                .format(i + 1)
                            raise OdkFormError(msg)
                elif token['token_type'] == 'begin repeat':
                    if not stack:
                        repeat = OdkRepeat(dict_row)
                        stack.append(repeat)
                    else:
                        msg = 'Unable to add repeat at row {}'.format(i + 1)
                        raise OdkFormError(msg)
                elif token['token_type'] == 'end repeat':
                    if stack and isinstance(stack[-1], OdkRepeat):
                        repeat = stack.pop()  # Stack guaranteed empty now.
                        result.append(repeat)
                    else:
                        msg = 'Mismatched "end repeat" at row {}'.format(i + 1)
                        raise OdkFormError(msg)
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
                        msg = 'Table found outside of field-list group at' \
                              ' row {}'
                        msg = msg.format(i + 1)
                        raise OdkFormError(msg)
                elif token['token_type'] == 'context group':
                    if any(d['name'] == dict_row['name']
                           for d in context_groups):
                        msg = 'A context group with this name already exists' \
                              ' in survey.'
                        raise OdkFormError(msg)
                    else:
                        this_context_group = {
                            'name': dict_row['name'],
                            'is_closed': False,
                            'data': dict_row
                        }
                        context_groups.append(this_context_group)
                    if stack and isinstance(stack[-1], OdkGroup):
                        msg = ('PPP does not allow a group nested in a '
                               'field-list group. See row {}').format(i + 1)
                        raise OdkFormError(msg)
                # Intentionally no handling for these types.
                elif token['token_type'] in OdkForm.unhandled_token_types:
                    OdkForm.conversion_info = {} \
                        if OdkForm.conversion_info is None \
                        else OdkForm.conversion_info
                    k = 'Unhandled Token Types'
                    if k not in OdkForm.conversion_info:
                        OdkForm.conversion_info[k] = []
                    if token['token_type'] not in OdkForm.conversion_info[k]:
                        OdkForm.conversion_info[k].append(token['token_type'])
                else:
                    OdkForm.warnings = {} if OdkForm.warnings is None \
                        else OdkForm.warnings
                    k = 'Unknown Token Types'
                    if k not in OdkForm.warnings:
                        OdkForm.warnings[k] = []
                    if token['token_type'] not in OdkForm.warnings[k]:
                        OdkForm.warnings[k].append(token['token_type'])
        except KeyError:  # No survey found.
            pass
        return result
