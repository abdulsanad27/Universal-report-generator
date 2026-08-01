"""Structure-driven fallback parser for line-oriented test reports."""

import re
from collections import OrderedDict

from .base_parser import BaseParser


class GenericTXTParser(BaseParser):
    _STATUS = r"PASS(?:ED)?|SUCCESS|OK|TRUE|FAIL(?:ED|URE)?|ERROR|EXCEPTION|ASSERTION|TIMEOUT|ABORTED|SKIP(?:PED)?|IGNORED|DISABLED|NOT[ _-]?RUN"
    _STATUS_FIRST = re.compile(rf"^\s*(?P<status>{_STATUS})\b[\s:|,-]+(?P<test>[^|,\s]+)(?P<tail>.*)$", re.I)
    _STATUS_LAST = re.compile(rf"(?P<test>[\w.$]+[#$][\w$<>-]+).*?\b(?P<status>{_STATUS})\b(?P<tail>.*)$", re.I)
    _DELIMITED = re.compile(rf"^\s*(?P<class>[\w.$]+)\s*[|,;]\s*(?P<method>[\w$<>-]+)\s*[|,;]\s*(?P<status>{_STATUS})(?P<tail>.*)$", re.I)
    _TIME = re.compile(r"(?:\b(?:time|duration|elapsed)\s*[:=]?\s*|\s)(\d+(?:\.\d+)?)\s*(?:ms|s|sec(?:onds)?)?\b", re.I)
    _HEADING = re.compile(r"^\s*(?:class|suite|module)\s*[:=]\s*([\w.$-]+)\s*$", re.I)
    _DIAGNOSTIC = re.compile(r"(?:exception|assertion|caused by:|\bat\s+[\w.$]+\(|error|failure)", re.I)

    def parse(self, file_bytes):
        report = self.create_report("txt", "Text Test Report")
        classes, current_class, active, extracted = OrderedDict(), "UnknownClass", None, 0
        for raw_line in self.decode_file(file_bytes).splitlines():
            line = raw_line.rstrip()
            if not line.strip():
                continue
            heading = self._HEADING.match(line)
            if heading:
                current_class = heading.group(1)
                continue
            parsed = self._parse_row(line, current_class)
            if parsed:
                classname, method, status, time = parsed
                active = self.create_test(method, classname, status, time)
                classes.setdefault(classname, self.create_class(classname)).add_test(active)
                extracted += 1
                continue
            if active is not None:
                active.logs.append(line)
                if self._DIAGNOSTIC.search(line):
                    if not active.message:
                        active.message = line.strip()
                    active.stacktrace = (active.stacktrace + "\n" + line.strip()).strip()
                    if active.status == "pass":
                        active.status = self.normalize_status("error")
        for class_result in classes.values():
            report.add_class(class_result)
        report.has_test_data = bool(extracted)
        report.parsing_metadata["extraction_statistics"] = {"strategy": "status_first_status_last_delimited", "test_records": extracted, "classes_extracted": len(classes)}
        return self.finalize_report(report)

    def _parse_row(self, line, current_class):
        match = self._DELIMITED.match(line)
        if match:
            return match.group("class"), match.group("method"), match.group("status"), self._time(match.group("tail"))
        match = self._STATUS_FIRST.match(line)
        if match:
            classname, method = self._split_test(match.group("test"), current_class)
            return classname, method, match.group("status"), self._time(match.group("tail"))
        match = self._STATUS_LAST.search(line)
        if match:
            classname, method = self._split_test(match.group("test"), current_class)
            return classname, method, match.group("status"), self._time(match.group("tail"))
        return None

    @staticmethod
    def _split_test(value, default_class):
        if "#" in value:
            return value.split("#", 1)
        if "$" in value:
            return value.rsplit("$", 1)
        if "." in value:
            return value.rsplit(".", 1)
        return default_class, value

    def _time(self, text):
        match = self._TIME.search(text)
        if not match:
            return 0
        value = self.safe_float(match.group(1))
        return value / 1000 if re.search(r"ms\b", text[match.start():match.end()], re.I) else value
