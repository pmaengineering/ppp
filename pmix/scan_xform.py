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

import os.path
import xml.etree.ElementTree as ElementTree

from scan_constants import placeholders, xml_ns
from scan_errors import XformError
from __init__ import __version__ as version


class Xform:

    def __init__(self, xlsform=None, filename=None, form_id=None):
        if xlsform is not None:
            self.filename = xlsform.outpath
            self.form_id = xlsform.form_id
        elif filename is not None:
            self.filename = filename
            short_filename = os.path.split(self.filename)[1]
            short_name = os.path.splitext(short_filename)[0]
            self.form_id = short_name if form_id is None else form_id
        self.data = []
        with open(self.filename) as f:
            self.data = list(f)

    def make_edits(self):
        self.newline_fix()
        self.remove_placeholders()
        self.inject_version()

    def newline_fix(self):
        self.data = [line.replace("&amp;#x", "&#x") for line in self.data]

    def remove_placeholders(self):
        new_data = []
        for line in self.data:
            for fluff in placeholders:
                line = line.replace(fluff, "")
            new_data.append(line)
        self.data = new_data

    def inject_version(self):
        version_stamp = '<!-- qtools2 v{} -->\n'.format(version)
        stamp_line_number = 1
        self.data.insert(stamp_line_number, version_stamp)

    def overwrite(self):
        with open(self.filename, 'w') as f:
            f.writelines(self.data)

    def get_xml_root(self):
        xml_text = ''.join(self.data)
        xml_root = ElementTree.fromstring(xml_text)
        return xml_root

    def get_instance_xml(self):
        xml_text = ''.join(self.data)
        root = ElementTree.fromstring(xml_text)
        query = ".//*[@id='{}']".format(self.form_id)
        instance_xml = root.find(query)
        if instance_xml is None:
            m = u'Unable to locate XML instance in "{}".'.format(self.filename)
            m += u' Please confirm instance ID in settings tab.'
            raise XformError(m)
        return instance_xml

    def discover_all(self, xpaths):
        outcomes = []
        msg = []
        xml_root = self.get_xml_root()
        instance = self.get_instance_xml()
        for xpath in xpaths:
            discovered = self.discover_xpath(xpath, instance)
            outcomes.append(discovered)
            if discovered:
                try:
                    self.check_bind_attr(xpath, xml_root)
                except XformError as e:
                    msg.append(str(e))
        return outcomes, msg

    def has_logging(self):
        ns_key = xml_ns.keys()[0]
        logging_xpath = './{}:meta/{}:logging'.format(ns_key, ns_key)
        instance = self.get_instance_xml()
        found = instance.find(logging_xpath, xml_ns)
        return found is not None

    def check_bind_attr(self, xpath, xml_root):
        self.check_bind_relevant(xpath, xml_root)
        self.check_bind_calculate(xpath, xml_root)

    def check_bind_calculate(self, xpath, xml_root):
        this_bind = self.xpath_query(xpath, xml_root)
        if this_bind is not None:
            has_calculate = 'calculate' in this_bind.attrib
            if has_calculate:
                m = (u'In form_id "{}", linked xpath "{}" also defines a '
                     u'calculation.')
                m = m.format(self.form_id, xpath)
                raise XformError(m)
        else:
            # should never happen
            m = u'In form_id "{}", valid xpath "{}" has no associated <bind>'
            m = m.format(self.form_id, xpath)
            raise XformError(m)

    def check_bind_relevant(self, xpath, xml_root):
        # Must check ancestors (containing groups)
        xpath_split = xpath.split("/")
        for i in (j+1 for j in range(2, len(xpath_split))):
            xpath_to_check = "/".join(xpath_split[:i])
            this_bind = self.xpath_query(xpath_to_check, xml_root)
            if this_bind is not None:
                has_relevant = 'relevant' in this_bind.attrib
                if has_relevant and xpath_to_check == xpath:
                    m = (u'In form_id "{}", linked xpath "{}" also defines a '
                         u'relevant.')
                    m = m.format(self.form_id, xpath)
                    raise XformError(m)
                elif has_relevant:  # and xpath_to_check != xpath:
                    m = (u'In form_id "{}", ancestor xpath "{}" of linked '
                         u'xpath "{}" also defines a relevant.')
                    m = m.format(self.form_id, xpath_to_check, xpath)
                    raise XformError(m)
            elif xpath_to_check == xpath:  # and this_bind is None:
                # should never happen
                m = (u'In form_id "{}", valid xpath "{}" has no associated '
                     u'<bind>')
                m = m.format(self.form_id, xpath)
                raise XformError(m)

    @staticmethod
    def xpath_query(xpath, xml_root):
        ns_key = xml_ns.keys()[0]
        query = ".//{}:bind[@nodeset='{}']".format(ns_key, xpath)
        found = xml_root.find(query, xml_ns)
        return found

    @staticmethod
    def discover_xpath(xpath, instance):
        result = False
        try:
            full_root, full_xpath = Xform.convert_xpath(xpath)
            found = instance.find(full_xpath, xml_ns)
            roots_match = full_root == instance.tag
            result = found is not None and roots_match
        except (IndexError, SyntaxError):
            # Unable to split properly, bad xpath syntax
            pass
        return result

    @staticmethod
    def convert_xpath(xpath):
        strsplit = xpath.split('/')
        ns_key = xml_ns.keys()[0]
        ns_val = xml_ns[ns_key]
        root = strsplit[1]
        full_root = '{{{0}}}{1}'.format(ns_val, root)
        descendants = strsplit[2:]
        full_descendants = [':'.join([ns_key, d]) for d in descendants]
        full_xpath = './' + '/'.join(full_descendants)
        return full_root, full_xpath
