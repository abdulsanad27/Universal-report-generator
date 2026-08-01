"""Format-independent extraction and normalization of failure details."""

import re
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class FailureDetails:
    message: str
    stacktrace: str


class FailureDetailsExtractor:
    """Build a consistent failure payload from structured or line-based sources.

    Parsers may pass an XML failure node's text, a JSON message/stacktrace,
    HTML cell content, or accumulated log lines.  The extractor deliberately
    has no knowledge of report family, so additions improve every parser.
    """

    NO_DETAILS = "No failure details found in source report."
    _SIGNAL = re.compile(
        r"(?:\b(?:assertion(?:error)?|exception|error|failure|timeout|aborted|fatal)\b|"
        r"\bcaused by:\b|^\s*at\s+[\w.$]+\()", re.IGNORECASE,
    )

    @classmethod
    def extract(cls, message="", stacktrace="", *sources) -> FailureDetails:
        """Return non-empty, display-ready details for a failed test."""
        message = cls._clean(message)
        stacktrace = cls._clean(stacktrace)
        source_lines = cls._lines(sources)

        if not message:
            message = cls._best_message(source_lines)
        if not stacktrace:
            diagnostic_lines = [line for line in source_lines if cls._SIGNAL.search(line)]
            # Retain surrounding context where diagnostic classification is not
            # possible (for example, a vendor-specific abort reason).
            stacktrace = "\n".join(diagnostic_lines or source_lines)
        if not message and stacktrace:
            message = stacktrace.splitlines()[0].strip()
        if not message and not stacktrace:
            message = cls.NO_DETAILS
        return FailureDetails(message=message or cls.NO_DETAILS, stacktrace=stacktrace)

    @classmethod
    def enrich_test(cls, test):
        """Populate a failed ``TestResult`` from all information it retains."""
        if test.status != "fail":
            return test
        details = cls.extract(
            test.message, test.stacktrace, test.system_err, test.system_out,
            getattr(test, "errors", []), getattr(test, "logs", []),
        )
        test.message, test.stacktrace = details.message, details.stacktrace
        return test

    @classmethod
    def enrich_report(cls, report):
        for class_result in report.classes:
            for test in class_result.tests:
                cls.enrich_test(test)
        return report

    @staticmethod
    def _clean(value):
        return str(value).strip() if value is not None else ""

    @classmethod
    def _lines(cls, sources: Iterable):
        lines = []
        for source in sources:
            if isinstance(source, (list, tuple)):
                lines.extend(cls._lines(source))
            else:
                text = cls._clean(source)
                lines.extend(line.strip() for line in text.splitlines() if line.strip())
        return lines

    @classmethod
    def _best_message(cls, lines):
        return next((line for line in lines if cls._SIGNAL.search(line)), lines[0] if lines else "")
