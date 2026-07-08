import re
from collections import OrderedDict

from parsers.base_parser import BaseParser

from models.report import Report
from models.class_result import ClassResult
from models.test_result import TestResult


class EventLogParser(BaseParser):
    """
    Parses TradeFed event-logs.txt

    Example:

    - test: com.android.car.settings.bluetooth.BluetoothUtilsTest#testClearCache (status=PASSED)

    - test: com.android.car.settings.bluetooth.BluetoothUtilsTest#testUpdateCache (status=FAILED)
    """

    TEST_PATTERN = re.compile(
        r"- test:\s+(.*?)#(.*?)\s+\(status=(.*?)\)"
    )

    STATUS_MAP = {
        "PASSED": "pass",
        "FAILED": "fail",
        "IGNORED": "skip",
        "SKIPPED": "skip"
    }

    def parse(self, file_bytes):

        text = self.decode_file(file_bytes)

        report = Report()

        report.report_type = "tradefed_event"

        report.suite_name = "TradeFed Event Log"

        classes = OrderedDict()

        for line in text.splitlines():

            match = self.TEST_PATTERN.search(line)

            if not match:
                continue

            full_class = match.group(1).strip()

            function = match.group(2).strip()

            status = match.group(3).strip().upper()

            class_name = full_class.split(".")[-1]

            if class_name not in classes:

                classes[class_name] = ClassResult(
                    name=class_name
                )

            test = TestResult(

                name=function,

                classname=class_name,

                status=self.STATUS_MAP.get(
                    status,
                    "unknown"
                ),

                time=0.0,

                message="",

                stacktrace=""

            )

            classes[class_name].add_test(test)

        for cls in classes.values():

            report.add_class(cls)

        report.sort_classes()

        return report