import json

from .base_parser import BaseParser

from models.report import Report
from models.class_result import ClassResult
from models.test_result import TestResult


class JsonParser(BaseParser):

    def parse(self, file_bytes):

        try:
            text = self.decode_file(file_bytes)
            data = json.loads(text)

        except Exception as e:
            raise Exception(f"Invalid JSON file : {e}")

        report = Report()

        report.report_type = "json"

        report.suite_name = data.get(
            "suite_name",
            "JSON Test Report"
        )

        report.timestamp = data.get(
            "timestamp",
            ""
        )

        classes = data.get("classes", [])

        for cls in classes:

            class_result = ClassResult(

                name=cls.get(
                    "name",
                    "UnknownClass"
                )

            )

            tests = cls.get(
                "tests",
                []
            )

            for t in tests:

                test = TestResult(

                    name=t.get(
                        "name",
                        "Unnamed Test"
                    ),

                    classname=class_result.name,

                    status=t.get(
                        "status",
                        "pass"
                    ).lower(),

                    time=float(
                        t.get(
                            "time",
                            0
                        )
                    ),

                    message=t.get(
                        "message",
                        ""
                    ),

                    stacktrace=t.get(
                        "stacktrace",
                        ""
                    ),

                    system_out=t.get(
                        "system_out",
                        ""
                    ),

                    system_err=t.get(
                        "system_err",
                        ""
                    )

                )

                class_result.add_test(test)

            report.add_class(class_result)

        report.sort_classes()

        return report