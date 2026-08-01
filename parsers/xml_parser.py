"""Namespace-aware, recovery-oriented parser for JUnit and Android XML."""

import re
import xml.etree.ElementTree as ET
from collections import OrderedDict

from .base_parser import BaseParser


class XmlParser(BaseParser):
    """Extract JUnit-style test cases using strict then recovery strategies."""

    _CASE_START = re.compile(r"<testcase\b(?P<attributes>[^>]*)>", re.I)
    _CASE_EMPTY = re.compile(r"<testcase\b(?P<attributes>[^>]*)/\s*>", re.I)
    _ATTRIBUTE = re.compile(r'''([\w:.-]+)\s*=\s*["']([^"']*)["']''')

    def parse(self, file_bytes):
        text = self.decode_file(file_bytes)
        try:
            return self._parse_tree(file_bytes, text)
        except ET.ParseError:
            return self._parse_recovery(text)

    def _parse_tree(self, file_bytes, text):
        root = self._root(file_bytes, text)
        root_name = self.local_name(root.tag)
        if root_name not in {"testsuite", "testsuites"}:
            raise ValueError(f"Unsupported XML root: {root_name}")
        report = self.create_report("xml", root.get("name", "Test Report"), root.get("timestamp", ""))
        classes = OrderedDict()
        cases = [node for node in root.iter() if self.local_name(node.tag) == "testcase"]
        for testcase in cases:
            test = self._test_from_node(testcase)
            class_result = classes.setdefault(test.classname, self.create_class(test.classname))
            class_result.add_test(test)
        if not cases:
            self.add_diagnostic(report, "warnings", "XML contains no testcase nodes.")
        self._finish(report, classes, "xml_tree", len(cases))
        return report

    def _test_from_node(self, testcase):
        children = {self.local_name(child.tag): child for child in testcase}
        # Required outcome precedence: failure, error, result, skipped, status.
        outcome = "pass"
        detail = None
        if "failure" in children:
            outcome, detail = "failure", children["failure"]
        elif "error" in children:
            outcome, detail = "error", children["error"]
        elif testcase.get("result") is not None:
            outcome = testcase.get("result")
        elif "skipped" in children:
            outcome, detail = "skipped", children["skipped"]
        elif testcase.get("status") is not None:
            outcome = testcase.get("status")

        classname = (testcase.get("classname") or testcase.get("class") or
                     testcase.get("package") or "UnknownClass")
        name = testcase.get("name") or testcase.get("method") or "Unnamed Test"
        message, stacktrace = self._failure_details(detail)
        test = self.create_test(name, classname, outcome, testcase.get("time", 0),
                                message=message, stacktrace=stacktrace,
                                system_out=self._child_text(children.get("system-out")),
                                system_err=self._child_text(children.get("system-err")))
        return test

    def _parse_recovery(self, text):
        """Recover complete testcase fragments from an otherwise malformed XML file."""
        report = self.create_report("xml", "Recovered XML Test Report")
        classes = OrderedDict()
        recovered = 0
        for match in self._CASE_EMPTY.finditer(text):
            self._add_recovered_case(report, classes, match.group("attributes"), "")
            recovered += 1
        for match in self._CASE_START.finditer(text):
            if match.group("attributes").rstrip().endswith("/"):
                continue
            end = re.search(r"</testcase\s*>", text[match.end():], re.I)
            if end is None:
                continue
            body = text[match.end():match.end() + end.start()]
            self._add_recovered_case(report, classes, match.group("attributes"), body)
            recovered += 1
        self.add_diagnostic(report, "warnings", "Malformed XML recovered using testcase fragments.")
        self._finish(report, classes, "xml_fragment_recovery", recovered)
        return report

    def _add_recovered_case(self, report, classes, raw_attributes, body):
        attributes = dict(self._ATTRIBUTE.findall(raw_attributes))
        lower = body.lower()
        if "<failure" in lower:
            outcome = "failure"
        elif "<error" in lower:
            outcome = "error"
        elif attributes.get("result") is not None:
            outcome = attributes["result"]
        elif "<skipped" in lower:
            outcome = "skipped"
        else:
            outcome = attributes.get("status", "pass")
        message = self._attribute_from_tag(body, "failure", "message") or self._attribute_from_tag(body, "error", "message")
        stacktrace = self.clean_text(re.sub(r"<[^>]+>", "", body))
        classname = attributes.get("classname", attributes.get("class", "UnknownClass"))
        test = self.create_test(attributes.get("name", "Unnamed Test"), classname, outcome,
                                attributes.get("time", 0), message=message, stacktrace=stacktrace)
        classes.setdefault(classname, self.create_class(classname)).add_test(test)

    def _finish(self, report, classes, strategy, count):
        for class_result in classes.values():
            report.add_class(class_result)
        report.has_test_data = bool(count)
        report.parsing_metadata["extraction_statistics"] = {
            "strategy": strategy, "testcases_extracted": count, "classes_extracted": len(classes),
        }
        self.finalize_report(report)

    @staticmethod
    def _root(file_bytes, text):
        try:
            return ET.fromstring(file_bytes)
        except ET.ParseError:
            return ET.fromstring(text)

    def _failure_details(self, node):
        if node is None:
            return "", ""
        message = self.clean_text(node.get("message") or node.get("type"))
        text = self._child_text(node)
        if not message and text:
            message = text.splitlines()[0].strip()
        return message, text

    @staticmethod
    def _child_text(node):
        return "" if node is None else "\n".join(part.strip() for part in node.itertext() if part.strip())

    @staticmethod
    def _attribute_from_tag(body, tag, attribute):
        match = re.search(rf"<{tag}\b[^>]*\b{attribute}=[\"']([^\"']*)", body, re.I)
        return match.group(1) if match else ""
