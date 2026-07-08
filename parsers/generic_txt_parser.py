from collections import OrderedDict

from .base_parser import BaseParser

from models.report import Report
from models.class_result import ClassResult
from models.test_result import TestResult


class GenericTXTParser(BaseParser):

    def parse(self, file_bytes):

        text = self.decode_file(file_bytes)

        report = Report()

        report.report_type = "txt"

        report.suite_name = "Text Test Report"

        report.timestamp = ""

        classes = OrderedDict()

        current_class = None

        lines = text.splitlines()

        i = 0

        while i < len(lines):

            line = lines[i].strip()

            if line == "":

                i += 1
                continue

            # -------------------------
            # Class Name
            # -------------------------

            if (
                " " not in line
                and "." not in line
                and "#" not in line
                and ":" not in line
            ):

                current_class = line

                if current_class not in classes:

                    classes[current_class] = ClassResult(
                        name=current_class
                    )

                i += 1
                continue

            # -------------------------
            # PASS / FAIL / SKIP
            # -------------------------

            parts = line.split()

            if len(parts) >= 2:

                status = parts[0].upper()

                if status in ["PASS", "FAIL", "SKIP"]:

                    function = parts[1]

                    execution_time = 0

                    if len(parts) >= 3:

                        try:

                            execution_time = float(parts[2])

                        except:

                            execution_time = 0

                    message = ""

                    stacktrace = ""

                    # -------------------------
                    # Read failure lines
                    # -------------------------

                    if status == "FAIL":

                        failure_lines = []

                        j = i + 1

                        while j < len(lines):

                            next_line = lines[j].rstrip()

                            if next_line == "":

                                break

                            upper = next_line.upper()

                            if upper.startswith("PASS") \
                                    or upper.startswith("FAIL") \
                                    or upper.startswith("SKIP"):

                                break

                            failure_lines.append(next_line)

                            j += 1

                        if failure_lines:

                            message = failure_lines[0]

                            if len(failure_lines) > 1:

                                stacktrace = "\n".join(
                                    failure_lines[1:]
                                )

                        i = j - 1

                    if current_class is None:

                        current_class = "UnknownClass"

                        if current_class not in classes:

                            classes[current_class] = ClassResult(
                                name=current_class
                            )

                    test = TestResult(

                        name=function,

                        classname=current_class,

                        status=status.lower(),

                        time=execution_time,

                        message=message,

                        stacktrace=stacktrace

                    )

                    classes[current_class].add_test(test)

            i += 1

        for cls in classes.values():

            report.add_class(cls)

        report.sort_classes()

        return report