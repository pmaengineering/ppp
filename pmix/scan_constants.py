# The MIT License (MIT)
#
# Copyright (c) 2016 PMA2020
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


country_codes = {
    "Burkina Faso": "BF",
    "DR Congo": "CD",
    "Ethiopia": "ET",
    "Ghana": "GH",
    "Indonesia": "ID",
    "Kenya": "KE",
    "Niger": "NE",
    "Nigeria": "NG",
    "Uganda": "UG",
    "Rajasthan": "RJ",
    "Ivory Coast": "CI"
}


q_codes = {
    "Household-Questionnaire": "HQ",
    "Female-Questionnaire": "FQ",
    "SDP-Questionnaire": "SQ",
    "Listing": "listing",
    "Selection": "sel",
    "Reinterview-Questionnaire": "RQ"
}


xml_codes = {
    "HQ": "HHQ",
    "FQ": "FRS",
    "SQ": "SDP",
    "listing": "listing",
    "sel": "Selection",
    "RQ": "RQ"
}


"""
Regular expressions defining the formulation of form file names and XLSForm
metadata (and approval date)
"""
approval_date = 'May 2015'
form_title_model = "[CC]R[#]-[((Household|Female|SDP|Reinterview)-Questionnaire)|Selection|Listing]-v[##]"
form_id_model = "[HQ|FQ|SQ|RQ|listing|sel]-[cc]r[#]-v[##]"
odk_file_model = form_title_model + "-[SIG]"
form_title_re = "(" + "|".join(country_codes.values()) + ")R\\d{1,2}-(" + "|".join(q_codes.keys()) + ")-v\\d{1,2}"
form_id_re = "(" + "|".join(q_codes.values()) + ")-(" + "|".join([code.lower() for code in country_codes.values()]) + \
             ")r\\d{1,2}-v\\d{1,2}"
odk_file_re = form_title_re + "-[a-zA-Z]{2,}"


"""
A list of strings to delete from the questionnaires. These are just place
holders.
"""
placeholders = ("#####",)


"""
Constants used throughout the package
"""
XML_EXT = u'.xml'

SURVEY = u'survey'
CHOICES = u'choices'
SETTINGS = u'settings'
EXTERNAL_CHOICES = u'external_choices'
EXTERNAL_TYPES = [u'select_one_external', u'select_multiple_external']

SAVE_INSTANCE = u'save_instance'
SAVE_FORM = u'save_form'
DELETE_FORM = u'delete_form'
TYPE = u'type'
LIST_NAME = u'list_name'
NAME = u'name'

FORM_ID = u'form_id'
FORM_TITLE = u'form_title'
XML_ROOT = u'xml_root'
LOGGING = u'logging'

ITEMSETS = u'itemsets.csv'
MEDIA_DIR_EXT = u'-media'

# Command-line interface keywords
SUFFIX = u'suffix'
PREEXISTING = u'preexisting'
PMA = u'pma'
CHECK_VERSIONING = u'check_versioning'
STRICT_LINKING = u'strict_linking'
VALIDATE = u'validate'
EXTRAS = u'extras'
DEBUG = u'debug'

"""
Must be a dictionary with exactly one key-value pair. Used in searching within
an Xform
"""
xml_ns = {'h': 'http://www.w3.org/2002/xforms'}
