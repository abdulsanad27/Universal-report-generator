"""Multi-strategy extraction of TradeFed event logs."""

import re
from collections import OrderedDict

from parsers.base_parser import BaseParser


class EventLogParser(BaseParser):
    """Parse result records and their following diagnostic blocks."""

    _RESULT_PATTERNS = (
        re.compile(r"-\s*test:\s*(?P<class>[\w.$]+)#(?P<method>[\w$<>-]+).*?\(\s*status\s*=\s*(?P<status>[\w -]+)\s*\)", re.I),
        re.compile(r"\btest\s*[:=]\s*(?P<class>[\w.$]+)[#.]?(?P<method>[\w$<>-]+)\s+(?:result|status)\s*[:=]\s*(?P<status>[\w -]+)", re.I),
        re.compile(r"\b(?:testEnded|test_result|testResult)\s*\(?(?P<class>[\w.$]+)#(?P<method>[\w$<>-]+).*?(?:status|result)\s*[:=]\s*(?P<status>[\w -]+)", re.I),
    )
    _START_PATTERNS = (
        re.compile(r"\b(?:testStarted|test_started)\s*\(?(?P<class>[\w.$]+)#(?P<method>[\w$<>-]+)", re.I),
        re.compile(r"\btest\s*[:=]\s*(?P<class>[\w.$]+)#(?P<method>[\w$<>-]+)\s+(?:started|running)\b", re.I),
    )
    _BOUNDARY = re.compile(r"\b(?:next\s+(?:test|class|module)|(?:test|module|invocation)[_ ](?:started|ended|finished)|invocation finished)\b", re.I)
    _MODULE = re.compile(r"\bmodule\s*[:=]\s*([^\s,]+)", re.I)
    _TIME = re.compile(r"\b(?:time|duration|elapsed)\s*[:=]\s*(\d+(?:\.\d+)?)", re.I)
    _DIAGNOSTIC = re.compile(r"(?:exception|assertion|caused by:|\bat\s+[\w.$]+\(|error|failure)", re.I)

    def parse(self, file_bytes):
        report = self.create_report("tradefed_event", "TradeFed Event Log")
        classes, active, extracted = OrderedDict(), None, 0
        module = ""
        for raw_line in self.decode_file(file_bytes).splitlines():
            line = raw_line.rstrip()
            module_match = self._MODULE.search(line)
            if module_match:
                module = module_match.group(1)
                report.run_information.module = module
            result = self._match(self._RESULT_PATTERNS, line)
            if result:
                active = self._add_result(classes, result, module)
                extracted += 1
                continue
            start = self._match(self._START_PATTERNS, line)
            if start:
                active = self._add_started(classes, start, module)
                extracted += 1
                continue
            if active is not None:
                if self._BOUNDARY.search(line):
                    active = None
                elif line.strip():
                    self._append_context(active, line)

        for class_result in classes.values():
            report.add_class(class_result)
        report.has_test_data = bool(extracted)
        report.parsing_metadata["extraction_statistics"] = {
            "strategy": "event_result_and_lifecycle", "test_records": extracted,
            "classes_extracted": len(classes), "module": module,
        }
        return self.finalize_report(report)

    def _add_result(self, classes, match, module):
        test = self._add_test(classes, match.group("class"), match.group("method"), match.group("status"))
        test.time = self.safe_float(self._time(match.string))
        if module:
            test.logs.append(f"Module: {module}")
        return test

    def _add_started(self, classes, match, module):
        test = self._add_test(classes, match.group("class"), match.group("method"), "pass")
        if module:
            test.logs.append(f"Module: {module}")
        return test

    def _add_test(self, classes, classname, method, status):
        classname = self.clean_text(classname, "UnknownClass")
        class_result = classes.setdefault(classname, self.create_class(classname))
        test = self.create_test(method, classname, status)
        class_result.add_test(test)
        return test

    def _append_context(self, test, line):
        test.logs.append(line)
        if self._DIAGNOSTIC.search(line):
            if not test.message:
                test.message = line.strip()
            test.stacktrace = (test.stacktrace + "\n" + line.strip()).strip()
            # A failure diagnostic after a lifecycle start is authoritative.
            if test.status == "pass":
                test.status = self.normalize_status("error")

    @staticmethod
    def _match(patterns, line):
        return next((match for pattern in patterns if (match := pattern.search(line))), None)

    def _time(self, line):
        match = self._TIME.search(line)
        return match.group(1) if match else 0
