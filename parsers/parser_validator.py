"""Validation rules used before accepting a parser result."""

from models.report import Report
from .failure_details_extractor import FailureDetailsExtractor


class ParserValidator:
    """Validate reports without changing the report model's public API."""

    @staticmethod
    def is_valid(report, require_test_data=True):
        FailureDetailsExtractor.enrich_report(report)
        if not isinstance(report, Report) or not report.classes:
            return False
        tests = [test for cls in report.classes for test in cls.tests]
        if require_test_data and not tests:
            return False
        valid = all(
            test.name and test.classname and test.status in {"pass", "fail", "skip"}
            for test in tests
        )
        if not valid:
            return False
        for test in tests:
            if test.status == "fail" and not (test.message or test.stacktrace):
                return False
        parsed_total = len(tests)
        if report.summary_total and report.summary_total < parsed_total:
            ParserValidator._warning(report, "Reported total is smaller than extracted test count.")
        if report.summary_total and report.summary_total != report.summary_passed + report.summary_failed + report.summary_skipped:
            ParserValidator._warning(report, "Reported summary counts do not add up to reported total.")
        return True

    @staticmethod
    def _warning(report, message):
        metadata = getattr(report, "parsing_metadata", None)
        if metadata is not None and message not in metadata.setdefault("warnings", []):
            metadata["warnings"].append(message)
