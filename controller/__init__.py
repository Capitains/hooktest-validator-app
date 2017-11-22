from HookTest.capitains_units.cts import CTSMetadata_TestUnit, CTSText_TestUnit, CapitainsCtsText
from flask_babel import gettext
from lxml.etree import parse, ElementTree
from io import BytesIO


class AppError(Exception):
    def __init__(self, message="", *args):
        self.__message__ = message
        super(AppError, self).__init__(message, *args)

    @property
    def message(self):
        return self.__message__


class MissingField(AppError):
    """ When a field is missing """
    @property
    def message(self):
        return gettext("Field %(field)s is empty", field=self.__message__)


class XMLParsingError(AppError):
    """ When a field is missing """
    @property
    def message(self):
        return gettext("There was an error parsing the XML")


def router(form_data):
    """ Dispatches form_data to different test functions

    :param form_data:
    :type form_data: dict
    :returns: Template variables
    :rtype: dict
    """
    resource_type = form_data.get("resource_type", None)
    resource = form_data.get("resource", None)
    if not resource:
        raise MissingField(gettext("XML Resource"))
    elif not resource_type:
        raise MissingField(gettext("Resource Type"))
    resource = resource.strip()
    if resource_type == "cts_metadata":
        return textgroup_eval(resource)
    elif resource_type == "cts_epidoc":
        return cts_text_eval(resource, "epidoc")
    elif resource_type == "cts_tei":
        return cts_text_eval(resource, "tei")
    return {}


def test(obj):
    data = []
    for test in obj.tests:
        for status in getattr(obj, test)():
            data.append((obj.readable[test], status, [log.replace(">", "") for log in obj.logs]))
            obj.flush()
    return data


def advanced_test(obj):
    data = []
    i = 0
    for test in obj.tests:
        # Show the logs and return the status
        status = False not in [status for status in getattr(obj, test)()]
        obj.test_status[test] = status
        data.append((CTSText_TestUnit.readable[test], status, obj.logs))
        if test in obj.breaks and status == False:
            for t in obj[i+1:]:
                obj.test_status[t] = False
                data.append((CTSText_TestUnit.readable[t], False, []))
            break
        obj.flush()
    return data


def xml_parser(xml):
    return parse(BytesIO(xml.encode()))


def textgroup_eval(xml):
    """ Evaluate how XML is correct regarding CapiTainS CTS Guidelines for CTS Textgroup"""
    test_unit = CTSMetadata_TestUnit("path")
    test_unit.tests = ["capitain", "metadata", "check_urns"]
    try:
        test_unit.xml = xml_parser(xml)
    except Exception as E:
        print(E)
        raise XMLParsingError()
    return {
        "results": {gettext(readable): (status, logs) for readable, status, logs in test(test_unit)}
    }


def cts_text_eval(xml, scheme="tei"):
    """ Evaluate how XML is correct regarding CapiTainS CTS Guidelines for CTS TEI Texts"""
    test_unit = CTSText_TestUnit("path")
    test_unit.tests = [
        # Retrieving the URN
        "has_urn", 'language',
        # Requires parsable
        "refsDecl", "passages", "unique_passage", "duplicate", "forbidden"
    ]
    test_unit.scheme = scheme
    try:
        test_unit.xml = xml_parser(xml)
        test_unit.Text = CapitainsCtsText(resource=test_unit.xml)
    except Exception as E:
        raise XMLParsingError()
    return {
        "results": {gettext(readable): (status, logs) for readable, status, logs in advanced_test(test_unit)}
    }