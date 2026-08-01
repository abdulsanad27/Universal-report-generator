"""Stateful, multi-layout parser for TradeFed host logs."""

import re
from collections import OrderedDict

from parsers.base_parser import BaseParser


class HostLogParser(BaseParser):
    _INVOCATION_START = re.compile(r"\bstarting invocation\b", re.I)
    _INVOCATION_END = re.compile(r"\b(?:invocation (?:finished|ended)|end of results|cleaning up builds)\b", re.I)
    _META = {"device": re.compile(r"\bdevice\s*[:=]\s*(.+)", re.I),
             "module": re.compile(r"\bmodule\s*[:=]\s*(.+)", re.I),
             "build": re.compile(r"\bbuild\s*[:=]\s*(.+)", re.I)}
    _STARTS = (re.compile(r"\b(?:modulelistener\.)?testStarted\((?P<class>[\w.$]+)#(?P<method>[\w$<>-]+)\)", re.I),
               re.compile(r"\btest[_ ]started\s*[:(]\s*(?P<class>[\w.$]+)#(?P<method>[\w$<>-]+)", re.I))
    _RESULTS = (re.compile(r"(?:\[\d+\s*/\s*\d+\]\s+)?(?P<class>[\w.$]+)#(?P<method>[\w$<>-]+).*?\b(?P<status>PASSED|PASS|SUCCESS|OK|FAILED|FAILURE|FAIL|ERROR|EXCEPTION|TIMEOUT|ABORTED|SKIPPED|IGNORED|DISABLED|NOTRUN)\b", re.I),
                re.compile(r"\btest(?:Ended|_ended|Result)\s*\(?(?P<class>[\w.$]+)#(?P<method>[\w$<>-]+).*?(?:status|result)\s*[:=]\s*(?P<status>[\w -]+)", re.I))
    _FAILURE_EVENT = re.compile(r"\b(?:testFailed|test_failure|test_assumption_failure)\s*\(?(?P<class>[\w.$]+)#(?P<method>[\w$<>-]+)?", re.I)
    _SUMMARY = re.compile(r"\b(?P<name>total(?:\s+tests?)?|passed|failed|failures?|skipped|ignored|disabled)\s*[:=]\s*(?P<count>\d+)", re.I)
    _TIME = re.compile(r"\b(?:time|duration|elapsed)\s*[:=]\s*(\d+(?:\.\d+)?)", re.I)
    _DIAGNOSTIC = re.compile(r"(?:exception|assertion|caused by:|\bat\s+[\w.$]+\(|\bfatal\b|\berror\b|\bfailure\b)", re.I)

    def parse(self, file_bytes):
        report = self.create_report("tradefed_host", "TradeFed Host Log")
        classes, active, extracted = OrderedDict(), None, 0
        summaries = {"total": 0, "passed": 0, "failed": 0, "skipped": 0}
        for raw in self.decode_file(file_bytes).splitlines():
            line = raw.rstrip()
            if not line.strip():
                continue
            report.run_information.started |= bool(self._INVOCATION_START.search(line))
            report.run_information.finished |= bool(self._INVOCATION_END.search(line))
            self._metadata(report, line)
            self._summary(line, summaries)
            result = self._match(self._RESULTS, line)
            if result:
                active = self._new_test(classes, result.group("class"), result.group("method"), result.group("status"), line)
                extracted += 1
                continue
            failure = self._FAILURE_EVENT.search(line)
            if failure:
                active = self._new_test(classes, failure.group("class"), failure.group("method") or "Unknown Test", "failure", line)
                extracted += 1
                continue
            started = self._match(self._STARTS, line)
            if started:
                active = self._new_test(classes, started.group("class"), started.group("method"), "pass", line)
                extracted += 1
                continue
            if active is not None:
                self._append_context(active, line)
            if self._DIAGNOSTIC.search(line):
                report.run_information.errors.append(line)
            elif re.search(r"\b(?:warn|warning)\b", line, re.I):
                report.run_information.warnings.append(line)

        for class_result in classes.values():
            report.add_class(class_result)
        self._apply_summary(report, summaries, extracted)
        report.has_test_data = bool(extracted)
        report.parsing_metadata["extraction_statistics"] = {
            "strategy": "host_lifecycle_inline_and_summary", "test_records": extracted,
            "classes_extracted": len(classes), "summary": dict(summaries),
        }
        if not extracted:
            report.note = "This log contains invocation metadata but no recoverable test cases."
            self.add_diagnostic(report, "missing_fields", "No per-test result records found.")
        return self.finalize_report(report)

    def _new_test(self, classes, classname, method, status, line):
        classname = self.clean_text(classname, "UnknownClass")
        test = self.create_test(method, classname, status, self._time(line), message="", stacktrace="")
        classes.setdefault(classname, self.create_class(classname)).add_test(test)
        return test

    def _metadata(self, report, line):
        for attribute, pattern in self._META.items():
            match = pattern.search(line)
            if match:
                setattr(report.run_information, attribute, match.group(1).strip())

    def _summary(self, line, summaries):
        for match in self._SUMMARY.finditer(line):
            name, count = match.group("name").lower(), self.safe_int(match.group("count"))
            key = "total" if name.startswith("total") else "failed" if name.startswith("fail") else "skipped" if name in {"skipped", "ignored", "disabled"} else "passed"
            summaries[key] = count

    def _apply_summary(self, report, summaries, extracted):
        report.summary_total = summaries["total"]
        report.summary_passed = summaries["passed"]
        report.summary_failed = summaries["failed"]
        report.summary_skipped = summaries["skipped"]
        parsed = {"total": report.total if not summaries["total"] else extracted,
                  "passed": sum(t.status == "pass" for c in report.classes for t in c.tests),
                  "failed": sum(t.status == "fail" for c in report.classes for t in c.tests),
                  "skipped": sum(t.status == "skip" for c in report.classes for t in c.tests)}
        if extracted and summaries["total"] and summaries["total"] != extracted:
            self.add_diagnostic(report, "warnings", f"Summary total ({summaries['total']}) differs from extracted records ({extracted}).")
        if not summaries["total"] and extracted:
            report.summary_total = 0  # Report model derives all statistics from parsed tests.

    def _append_context(self, test, line):
        test.logs.append(line)
        if self._DIAGNOSTIC.search(line):
            if not test.message:
                test.message = line.strip()
            test.stacktrace = (test.stacktrace + "\n" + line.strip()).strip()
            if test.status == "pass":
                test.status = self.normalize_status("error")

    @classmethod
    def _match(cls, patterns, line):
        return next((match for pattern in patterns if (match := pattern.search(line))), None)

    def _time(self, line):
        match = self._TIME.search(line)
        return match.group(1) if match else 0
