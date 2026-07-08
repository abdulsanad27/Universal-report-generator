import re
from collections import OrderedDict

from parsers.base_parser import BaseParser

from models.report import Report
from models.class_result import ClassResult
from models.test_result import TestResult


class JavaLogParser(BaseParser):
    """
    Parses TradeFed isolated-java-logs.txt

    Captures:
        • Class execution
        • Test execution
        • Logs
        • Warnings
        • Errors
        • Exceptions
        • Stacktraces
    """

    CLASS_PATTERN = re.compile(
        r"Starting class:\s*(.*)"
    )

    TEST_PATTERN = re.compile(
        r"\[Robolectric\]\s*(.*)\.(.*)"
    )

    EXCEPTION_PATTERN = re.compile(
        r".*(Exception|AssertionError|Error):?.*"
    )

    STACK_PATTERN = re.compile(
        r"\s+at\s+.*"
    )

    WARNING_PATTERN = re.compile(
        r".*\bWARN\b.*|.*\bWARNING\b.*",
        re.IGNORECASE
    )

    ERROR_PATTERN = re.compile(
        r".*\bERROR\b.*|.*\bE/.*",
        re.IGNORECASE
    )

    LOG_PATTERN = re.compile(
        r".*\b(D|I|V|DEBUG|INFO)\b.*",
        re.IGNORECASE
    )

    DONE_PATTERN = re.compile(
        r"Done executing class"
    )

    def parse(self, file_bytes):

        text = self.decode_file(file_bytes)

        report = Report()

        report.report_type = "tradefed_java"

        report.suite_name = "TradeFed Java Log"

        classes = OrderedDict()

        current_class = None

        current_test = None

        collecting_stack = False

        for line in text.splitlines():

            line = line.rstrip()

            #
            # Starting Class
            #

            match = self.CLASS_PATTERN.search(line)

            if match:

                current_class = match.group(1).split(".")[-1]

                if current_class not in classes:

                    classes[current_class] = ClassResult(
                        name=current_class
                    )

                current_test = None

                collecting_stack = False

                continue

            #
            # Test Started
            #

            match = self.TEST_PATTERN.search(line)

            if match:

                cls = match.group(1).split(".")[-1]

                method = match.group(2)

                if cls not in classes:

                    classes[cls] = ClassResult(
                        name=cls
                    )

                current_class = cls

                current_test = TestResult(

                    name=method,

                    classname=cls,

                    status="pass"

                )

                classes[cls].add_test(current_test)

                collecting_stack = False

                continue

            #
            # Exception
            #

            if current_test:

                if self.EXCEPTION_PATTERN.match(line):

                    current_test.status = "fail"

                    current_test.message = line.strip()

                    collecting_stack = True

                    continue

            #
            # Stacktrace
            #

            if current_test and collecting_stack:

                if self.STACK_PATTERN.match(line):

                    current_test.stacktrace += line + "\n"

                    continue

                else:

                    collecting_stack = False

            #
            # Warning
            #

            if current_test:

                if self.WARNING_PATTERN.match(line):

                    current_test.add_warning(line)

                    continue

            #
            # Error
            #

            if current_test:

                if self.ERROR_PATTERN.match(line):

                    current_test.add_error(line)

                    continue

            #
            # Normal Logs
            #

            if current_test:

                if self.LOG_PATTERN.match(line):

                    current_test.add_log(line)

                    continue

            #
            # Done
            #

            if self.DONE_PATTERN.search(line):

                current_test = None

                collecting_stack = False

        for cls in classes.values():

            report.add_class(cls)

        report.sort_classes()

        return report