import re
from collections import OrderedDict

from .base_parser import BaseParser

from models.report import Report
from models.class_result import ClassResult
from models.test_result import TestResult


class LogParser(BaseParser):

    def parse(self, file_bytes):

        text = self.decode_file(file_bytes)

        report = Report()

        report.report_type = "log"

        report.suite_name = "Log Test Report"

        report.timestamp = ""

        classes = OrderedDict()

        lines = text.splitlines()

        current_test = None

        current_class = None

        stacktrace = []

        for line in lines:

            line = line.rstrip()

            if not line:
                continue

            upper = line.upper()

            # ----------------------------------------------------
            # PASS
            # Example:
            # PASS ActivityLogicTest#formatMillis 0.002
            # ----------------------------------------------------

            if upper.startswith("PASS"):

                current_test = None

                stacktrace = []

                parts = line.split()

                if len(parts) >= 2:

                    location = parts[1]

                    time = 0

                    if len(parts) >= 3:

                        try:
                            time = float(parts[2])
                        except:
                            time = 0

                    if "#" in location:

                        current_class, function = location.split("#", 1)

                    elif "." in location:

                        current_class, function = location.rsplit(".", 1)

                    else:

                        current_class = "UnknownClass"

                        function = location

                    if current_class not in classes:

                        classes[current_class] = ClassResult(
                            name=current_class
                        )

                    test = TestResult(

                        name=function,

                        classname=current_class,

                        status="pass",

                        time=time

                    )

                    classes[current_class].add_test(test)

                continue

            # ----------------------------------------------------
            # SKIP
            # ----------------------------------------------------

            if upper.startswith("SKIP"):

                current_test = None

                stacktrace = []

                parts = line.split()

                if len(parts) >= 2:

                    location = parts[1]

                    time = 0

                    if len(parts) >= 3:

                        try:
                            time = float(parts[2])
                        except:
                            time = 0

                    if "#" in location:

                        current_class, function = location.split("#", 1)

                    elif "." in location:

                        current_class, function = location.rsplit(".", 1)

                    else:

                        current_class = "UnknownClass"

                        function = location

                    if current_class not in classes:

                        classes[current_class] = ClassResult(
                            name=current_class
                        )

                    test = TestResult(

                        name=function,

                        classname=current_class,

                        status="skip",

                        time=time

                    )

                    classes[current_class].add_test(test)

                continue

            # ----------------------------------------------------
            # FAIL
            # ----------------------------------------------------

            if upper.startswith("FAIL"):

                stacktrace = []

                parts = line.split()

                if len(parts) >= 2:

                    location = parts[1]

                    time = 0

                    if len(parts) >= 3:

                        try:
                            time = float(parts[2])
                        except:
                            time = 0

                    if "#" in location:

                        current_class, function = location.split("#", 1)

                    elif "." in location:

                        current_class, function = location.rsplit(".", 1)

                    else:

                        current_class = "UnknownClass"

                        function = location

                    if current_class not in classes:

                        classes[current_class] = ClassResult(
                            name=current_class
                        )

                    current_test = TestResult(

                        name=function,

                        classname=current_class,

                        status="fail",

                        time=time

                    )

                    classes[current_class].add_test(current_test)

                continue

            # ----------------------------------------------------
            # Failure Message
            # ----------------------------------------------------

            if current_test is not None:

                stacktrace.append(line)

                current_test.stacktrace = "\n".join(stacktrace)

                if current_test.message == "":

                    current_test.message = line

        for cls in classes.values():

            report.add_class(cls)

        report.sort_classes()

        return report