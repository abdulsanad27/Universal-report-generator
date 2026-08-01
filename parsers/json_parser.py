import json
from collections import OrderedDict

from .base_parser import BaseParser

from models.report import Report
from models.class_result import ClassResult
from models.test_result import TestResult


class JsonParser(BaseParser):

    def parse(self, file_bytes):

        text = self.decode_file(file_bytes)
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return self._recover_test_objects(text)
        if not isinstance(data, dict):
            raise ValueError("JSON report must be an object.")

        report = self.create_report("json", data.get("suite_name", data.get("testSuite", "JSON Test Report")),
                                    data.get("timestamp", ""))

        classes = data.get("classes", [])

        for cls in classes:

            if not isinstance(cls, dict):
                continue
            class_result = self.create_class(cls.get("name", "UnknownClass"))

            tests = cls.get(
                "tests",
                []
            )

            for t in tests:
                if not isinstance(t, dict):
                    continue

                test = self.create_test(t.get("name", "Unnamed Test"), class_result.name,
                                        t.get("status", "pass"), t.get("time", 0),
                                        message=t.get("message"), stacktrace=t.get("stacktrace"),
                                        system_out=t.get("system_out"), system_err=t.get("system_err"),
                                        exception=t.get("exception"), root_cause=t.get("root_cause"),
                                        reason=t.get("reason"), details=t.get("details"), failure=t.get("failure"))

                class_result.add_test(test)

            report.add_class(class_result)

        # Common flat JSON schemas store all tests in ``testCases`` (or
        # ``tests``), with the class name on each individual result.
        flat_tests = data.get("testCases", [])
        if not classes and isinstance(data.get("tests"), list):
            flat_tests = data["tests"]
        if isinstance(flat_tests, list):
            grouped = OrderedDict()
            for item in flat_tests:
                if not isinstance(item, dict):
                    continue
                classname = item.get("classname", item.get("className", "UnknownClass"))
                grouped.setdefault(classname, self.create_class(classname))
                grouped[classname].add_test(self.create_test(
                    item.get("name", "Unnamed Test"), classname,
                    item.get("status", "pass"), item.get("time", 0),
                    message=item.get("message"), stacktrace=item.get("stacktrace"),
                    system_out=item.get("system_out"), system_err=item.get("system_err")))
            for class_result in grouped.values():
                report.add_class(class_result)

        return self.finalize_report(report)

    def _recover_test_objects(self, text):
        """Recover individually valid test objects from a damaged JSON envelope."""
        decoder, records, offset = json.JSONDecoder(), [], 0
        while offset < len(text):
            start = text.find("{", offset)
            if start < 0:
                break
            try:
                value, end = decoder.raw_decode(text[start:])
            except json.JSONDecodeError:
                offset = start + 1
                continue
            offset = start + end
            if isinstance(value, dict) and {"name", "status"}.issubset(value):
                records.append(value)
        report = self.create_report("json", "Recovered JSON Test Report")
        grouped = OrderedDict()
        for item in records:
            classname = item.get("classname", item.get("className", "UnknownClass"))
            grouped.setdefault(classname, self.create_class(classname)).add_test(self.create_test(
                item.get("name", "Unnamed Test"), classname, item.get("status", "skip"), item.get("time", 0),
                message=item.get("message"), stacktrace=item.get("stacktrace"),
                system_out=item.get("system_out"), system_err=item.get("system_err"),
                exception=item.get("exception"), root_cause=item.get("root_cause"),
                reason=item.get("reason"), details=item.get("details"), failure=item.get("failure")))
        for class_result in grouped.values():
            report.add_class(class_result)
        report.has_test_data = bool(records)
        self.add_diagnostic(report, "warnings", "Malformed JSON recovered from complete embedded test objects.")
        report.parsing_metadata["extraction_statistics"] = {
            "strategy": "json_object_recovery", "testcases_extracted": len(records),
            "classes_extracted": len(grouped),
        }
        return self.finalize_report(report)
