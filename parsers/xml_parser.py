import xml.etree.ElementTree as ET

from collections import defaultdict

from .base_parser import BaseParser

from models.report import Report
from models.class_result import ClassResult
from models.test_result import TestResult


class XmlParser(BaseParser):

    def parse(self, file_bytes):

        root = ET.fromstring(file_bytes)

        report = Report()

        # ----------------------------------------
        # Detect Root
        # ----------------------------------------

        if root.tag == "testsuites":

            report.suite_name = root.get(
                "name",
                "Test Report"
            )

            report.timestamp = root.get(
                "timestamp",
                ""
            )

            suites = [
                child
                for child in root
                if child.tag == "testsuite"
            ]

        elif root.tag == "testsuite":

            report.suite_name = root.get(
                "name",
                "Test Report"
            )

            report.timestamp = root.get(
                "timestamp",
                ""
            )

            suites = [root]

        else:

            raise Exception(
                f"Unsupported XML Root : {root.tag}"
            )

        report.report_type = "xml"

        class_map = defaultdict(ClassResult)

        # ----------------------------------------
        # Parse Testcases
        # ----------------------------------------

        for suite in suites:

            for testcase in suite.findall("testcase"):

                classname = testcase.get(
                    "classname",
                    "(Unknown)"
                )

                if classname not in class_map:

                    class_map[classname] = ClassResult(
                        name=classname
                    )

                status = "pass"

                message = ""

                stacktrace = ""

                failure = testcase.find("failure")

                error = testcase.find("error")

                skipped = testcase.find("skipped")

                result = (
                    testcase.get("result", "")
                    .lower()
                )

                if failure is not None:

                    status = "fail"

                    if failure.get("message"):

                        message = failure.get("message")

                    if failure.text:

                        stacktrace = failure.text.strip()

                elif error is not None:

                    status = "fail"

                    if error.get("message"):

                        message = error.get("message")

                    if error.text:

                        stacktrace = error.text.strip()

                elif skipped is not None:

                    status = "skip"

                    if skipped.get("message"):

                        message = skipped.get("message")

                elif result in [

                    "failed",

                    "failure",

                    "error"

                ]:

                    status = "fail"

                elif result in [

                    "skip",

                    "skipped",

                    "disabled"

                ]:

                    status = "skip"

                test = TestResult(

                    name=testcase.get(
                        "name",
                        "(Unnamed Test)"
                    ),

                    classname=classname,

                    status=status,

                    time=float(
                        testcase.get(
                            "time",
                            0
                        )
                    ),

                    message=message,

                    stacktrace=stacktrace

                )

                class_map[classname].add_test(test)

        # ----------------------------------------
        # Add Classes
        # ----------------------------------------

        for cls in class_map.values():

            report.add_class(cls)

        report.sort_classes()

        return report