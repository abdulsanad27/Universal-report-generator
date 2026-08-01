"""Multi-signal structural identification of supported report families."""

import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class Detection:
    report_type: str
    confidence: float
    signals: tuple = field(default_factory=tuple)
    version: str = "unknown"


class ParserDetector:
    """Scores independent structural signals, never a filename or one keyword."""

    def detect(self, file_bytes: bytes, filename: str = "") -> List[Detection]:
        text = self._decode(file_bytes)
        scores: Dict[str, int] = {}
        signals: Dict[str, List[str]] = {}

        def add(kind, points, signal):
            scores[kind] = scores.get(kind, 0) + points
            signals.setdefault(kind, []).append(signal)

        data = self._json(text)
        if isinstance(data, (dict, list)):
            add("json", 45, "valid JSON document")
            if isinstance(data, dict):
                keys = {str(key).lower() for key in data}
                if keys & {"classes", "testcases", "tests", "suite_name", "testsuite"}:
                    add("json", 35, "test-report schema keys")
                if any(isinstance(value, (list, dict)) for value in data.values()):
                    add("json", 15, "structured test containers")
        elif text.lstrip().startswith(("{", "[")):
            json_signals = sum(marker in text.lower() for marker in (
                '"testcases"', '"classes"', '"classname"', '"status"', '"name"'))
            if json_signals >= 3:
                add("json", 55, "damaged JSON with repeated test-schema fields")

        root = self._xml_root(file_bytes, text)
        if root is not None:
            tag_names = [self._local_name(node.tag) for node in root.iter()]
            attrs = {key.lower() for node in root.iter() for key in node.attrib}
            if self._local_name(root.tag) in {"testsuite", "testsuites"}: add("xml", 30, "JUnit suite root")
            if "testcase" in tag_names: add("xml", 25, "testcase nodes")
            if "testsuite" in tag_names: add("xml", 15, "testsuite nodes")
            if {"failure", "error", "skipped"} & set(tag_names): add("xml", 10, "JUnit outcome nodes")
            if {"result", "status", "classname", "time"} & attrs: add("xml", 15, "JUnit attributes")
            if self._local_name(root.tag) == "configuration": add("tradefed_config", 55, "TradeFed configuration root")
            if "test" in tag_names and self._local_name(root.tag) == "configuration": add("tradefed_config", 25, "TradeFed test configuration")
        elif text.count("<testcase") >= 1 and text.count("<testsuite") >= 1:
            add("xml", 55, "damaged XML with suite and testcase structures")

        lower = text.lower()
        if "<html" in lower or "<!doctype html" in lower:
            add("html", 40, "HTML document root")
            if re.search(r"<table\b|role=[\"']table", lower): add("html", 25, "HTML table structure")
            if re.search(r"pass(?:ed)?|fail(?:ed|ure)?|skip(?:ped)?", lower): add("html", 15, "result vocabulary")

        self._score_tradefed(text, add)
        self._score_generic_text(text, add)
        if not scores:
            add("generic_txt", 1, "unclassified textual content")

        return [Detection(kind, min(100.0, score), tuple(signals[kind]), self._version(kind, text))
                for kind, score in sorted(scores.items(), key=lambda item: item[1], reverse=True)]

    def _score_tradefed(self, text, add):
        lower = text.lower()
        event_records = re.findall(r"-\s*test:\s+[\w.$]+#[\w$<>-]+.*?\bstatus\s*=", text, re.I)
        if event_records:
            # Prefix, test identifier and explicit status field are distinct
            # structural signals contained by each canonical event record.
            add("tradefed_event", min(75, 45 + len(event_records) * 10), "event test records with identifiers and statuses")
        event_patterns = [r"\btest_(?:started|failed|ended|ignored)\b", r"\bevent[-_ ]log\b", r"\b(?:module|invocation)\b"]
        matched = sum(bool(re.search(pattern, text, re.I)) for pattern in event_patterns)
        if matched >= 2: add("tradefed_event", 35 + matched * 15, f"{matched} event-log structures")

        host_patterns = [r"\bstarting invocation\b", r"\binvocation (?:finished|ended)\b", r"\b(?:module|invocation)listener\b", r"\b(?:atest|tradefed)\b", r"\btotal tests?\s*[:=]"]
        matched = sum(bool(re.search(pattern, text, re.I)) for pattern in host_patterns)
        if matched >= 2: add("tradefed_host", 25 + matched * 12, f"{matched} host-log structures")

        java_patterns = [r"\bstarting class:\b", r"\[robolectric\]", r"\bdone executing class\b", r"\bisolated-java-logs\b"]
        matched = sum(bool(re.search(pattern, text, re.I)) for pattern in java_patterns)
        if matched >= 2: add("tradefed_java", 30 + matched * 15, f"{matched} Java-log structures")

        entries = re.findall(r"(?m)^\s*[\w.$]+#[\w$]+\s*$", text)
        if len(entries) >= 2 and not re.search(r"\b(?:status|invocation|total tests)\b", lower):
            add("tradefed_passed", 70, "repeated class#method entries")

    @staticmethod
    def _score_generic_text(text, add):
        status_lines = re.findall(r"(?im)^\s*(?:pass(?:ed)?|success|ok|fail(?:ed|ure)?|error|exception|skip(?:ped)?|ignored|disabled)\b.*$", text)
        references = re.findall(r"[A-Za-z_$][\w.$]*[#$][A-Za-z_$][\w$]*", text)
        if len(status_lines) >= 2: add("generic_txt", 35, "repeated status rows")
        if len(references) >= 2: add("generic_txt", 25, "repeated test identifiers")
        if re.search(r"(?im)\b(?:duration|elapsed|time)\b", text): add("generic_txt", 10, "timing column vocabulary")

    @staticmethod
    def _version(kind, text):
        if kind.startswith("tradefed"):
            match = re.search(r"(?:tradefed|cts|atest)\s*(?:version\s*)?([\d.]+)", text, re.I)
            return match.group(1) if match else "unknown"
        return "unknown"

    @staticmethod
    def _decode(data):
        for encoding in ("utf-8-sig", "utf-16", "utf-16-le", "utf-16-be", "latin-1"):
            try: return data.decode(encoding)
            except UnicodeDecodeError: continue
        return ""

    @staticmethod
    def _json(text):
        try: return json.loads(text)
        except (TypeError, ValueError): return None

    @staticmethod
    def _xml_root(data, text):
        for source in (data, text):
            try: return ET.fromstring(source)
            except (ET.ParseError, ValueError): continue
        return None

    @staticmethod
    def _local_name(tag):
        return str(tag).rsplit("}", 1)[-1].lower()
