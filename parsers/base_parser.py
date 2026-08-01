from abc import ABC, abstractmethod

from models.report import Report
from models.class_result import ClassResult
from models.test_result import TestResult
from .status_normalizer import StatusNormalizer
from .failure_details_extractor import FailureDetailsExtractor


class BaseParser(ABC):
    """
    Base class for every parser.

    Every parser MUST inherit this class.
    """

    @abstractmethod
    def parse(self, file_bytes: bytes) -> Report:
        """
        Parse uploaded file and return Report object.
        """
        pass

    def decode_file(self, file_bytes: bytes) -> str:
        """
        Decode bytes safely.
        """

        encodings = [
            "utf-8-sig",
            "utf-8",
            "utf-16",
            "utf-16-le",
            "utf-16-be",
            "latin-1"
        ]

        for encoding in encodings:

            try:
                return file_bytes.decode(encoding)

            except UnicodeDecodeError:
                continue

        raise Exception("Unable to decode uploaded file.")

    def normalize_status(self, value, default="skip") -> str:
        """Return the model-compatible lower-case canonical status."""
        canonical_default = StatusNormalizer.normalize(default)
        return StatusNormalizer.normalize(value, canonical_default).lower()

    @staticmethod
    def safe_float(value, default=0.0) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def safe_int(value, default=0) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def clean_text(value, default="") -> str:
        if value is None:
            return default
        return str(value).strip()

    def create_test(self, name, classname, status="pass", time=0.0, **kwargs):
        test = TestResult(
            name=self.clean_text(name, "Unnamed Test"),
            classname=self.clean_text(classname, "UnknownClass"),
            status=self.normalize_status(status), time=self.safe_float(time),
            message=self.clean_text(kwargs.get("message")),
            stacktrace=self.clean_text(kwargs.get("stacktrace")),
            system_out=self.clean_text(kwargs.get("system_out")),
            system_err=self.clean_text(kwargs.get("system_err")),
        )
        if test.status == "fail":
            details = FailureDetailsExtractor.extract(
                test.message, test.stacktrace,
                *(value for key, value in kwargs.items()
                  if key not in {"message", "stacktrace", "system_out", "system_err"}),
            )
            test.message, test.stacktrace = details.message, details.stacktrace
        return FailureDetailsExtractor.enrich_test(test)

    @staticmethod
    def finalize_report(report):
        """Apply the common result contract before a parser returns a report."""
        FailureDetailsExtractor.enrich_report(report)
        report.sort_classes()
        return report

    def create_class(self, name):
        return ClassResult(name=self.clean_text(name, "UnknownClass"))

    def create_report(self, report_type, suite_name, timestamp=""):
        report = Report(report_type=report_type, suite_name=suite_name, timestamp=timestamp)
        # Dynamic diagnostics preserve the existing Report dataclass/API and
        # remain available to API callers without affecting templates.
        report.parsing_metadata = {
            "warnings": [], "missing_fields": [], "unsupported_sections": [],
            "extraction_statistics": {},
        }
        return report

    @staticmethod
    def add_diagnostic(report, category, message):
        metadata = getattr(report, "parsing_metadata", None)
        if metadata is not None:
            metadata.setdefault(category, []).append(message)

    @staticmethod
    def local_name(tag):
        return str(tag).rsplit("}", 1)[-1].lower()
