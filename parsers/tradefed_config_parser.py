import xml.etree.ElementTree as ET

from .base_parser import BaseParser

from models.report import Report
from models.class_result import ClassResult
from models.test_result import TestResult


class TradeFedConfigParser(BaseParser):
    """
    Parses TradeFed XML configuration files.

    These files describe the execution setup and do not contain test-case results,
    so the parser returns a lightweight report with a clear no-test-data note.
    """

    def parse(self, file_bytes):
        text = self.decode_file(file_bytes)

        report = Report()
        report.report_type = "tradefed_config"
        report.suite_name = "TradeFed Configuration"
        report.note = (
            "This XML file contains TradeFed configuration metadata rather than test-case results."
        )

        try:
            root = ET.fromstring(file_bytes)
        except ET.ParseError:
            root = ET.fromstring(text.encode("utf-8"))

        info = report.run_information
        info.information.append("TradeFed XML configuration detected")

        if root.tag == "configuration":
            for child in root:
                if child.tag == "test":
                    test_class = child.get("class", "")
                    if test_class:
                        info.information.append(f"Test runner: {test_class}")
                elif child.tag == "global_filters":
                    filters = [option.get("value", "") for option in child.findall("option") if option.get("value")]
                    if filters:
                        info.information.append("Global filters: " + ", ".join(filters))

        fallback_class = ClassResult(name="TradeFed Configuration")
        fallback_test = TestResult(
            name="Configuration Metadata",
            classname="TradeFed Configuration",
            status="pass",
            time=0.0,
            message="No test-case results were found in this configuration XML file.",
            stacktrace=""
        )
        fallback_class.add_test(fallback_test)
        report.add_class(fallback_class)

        return report
