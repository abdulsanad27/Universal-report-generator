from parsers.xml_parser import XmlParser
from parsers.json_parser import JsonParser
from parsers.html_parser import HtmlParser
from parsers.generic_txt_parser import GenericTXTParser

from parsers.tradefed.event_log_parser import EventLogParser
from parsers.tradefed.host_log_parser import HostLogParser
from parsers.tradefed.java_log_parser import JavaLogParser
from parsers.tradefed.passed_tests_parser import PassedTestsParser
from parsers.tradefed_config_parser import TradeFedConfigParser


class ParserFactory:

    @staticmethod
    def get_parser(report_type):

        parsers = {

            "xml": XmlParser(),

            "json": JsonParser(),

            "html": HtmlParser(),

            "generic_txt": GenericTXTParser(),

            "tradefed_event": EventLogParser(),

            "tradefed_host": HostLogParser(),

            "tradefed_java": JavaLogParser(),

            "tradefed_passed": PassedTestsParser(),

            "tradefed_config": TradeFedConfigParser()

        }

        parser = parsers.get(report_type)

        if parser is None:
            raise Exception(
                f"No parser found for '{report_type}'"
            )

        return parser