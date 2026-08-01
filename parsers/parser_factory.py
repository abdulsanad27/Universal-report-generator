"""Parser registration, confidence-based selection and safe fallback parsing."""

from parsers.xml_parser import XmlParser
from parsers.json_parser import JsonParser
from parsers.html_parser import HtmlParser
from parsers.generic_txt_parser import GenericTXTParser
from parsers.log_parser import LogParser
from parsers.tradefed.event_log_parser import EventLogParser
from parsers.tradefed.host_log_parser import HostLogParser
from parsers.tradefed.java_log_parser import JavaLogParser
from parsers.tradefed.passed_tests_parser import PassedTestsParser
from parsers.tradefed_config_parser import TradeFedConfigParser
from detector.parser_detector import ParserDetector
from .duplicate_detector import DuplicateDetector
from .parser_validator import ParserValidator


class ParserFactory:
    """Single extension point for supported parsers.

    ``get_parser`` remains available for existing callers. New ingestion should
    use ``parse`` so confidence ordering, validation, deduplication and fallback
    are applied consistently.
    """

    _PARSER_TYPES = {
        "xml": XmlParser, "json": JsonParser, "html": HtmlParser,
        "generic_txt": GenericTXTParser, "log": LogParser,
        "tradefed_event": EventLogParser, "tradefed_host": HostLogParser,
        "tradefed_java": JavaLogParser, "tradefed_passed": PassedTestsParser,
        "tradefed_config": TradeFedConfigParser,
    }

    @classmethod
    def get_parser(cls, report_type):
        parser_class = cls._PARSER_TYPES.get(report_type)
        if parser_class is None:
            raise ValueError(f"No parser found for '{report_type}'")
        return parser_class()

    @classmethod
    def parse(cls, file_bytes, filename="", preferred_type=None):
        """Parse with the strongest content match and retry invalid results."""
        detections = ParserDetector().detect(file_bytes, filename)
        candidates = [item.report_type for item in detections]
        if preferred_type in cls._PARSER_TYPES and preferred_type not in candidates:
            candidates.append(preferred_type)
        # Generic log parsing is a useful final fallback for status-based text.
        for fallback in ("generic_txt", "log"):
            if fallback not in candidates:
                candidates.append(fallback)

        errors = []
        for report_type in candidates:
            try:
                report = cls.get_parser(report_type).parse(file_bytes)
                DuplicateDetector.merge_report(report)
                if ParserValidator.is_valid(report):
                    detection = next((item for item in detections if item.report_type == report_type), None)
                    metadata = getattr(report, "parsing_metadata", {})
                    metadata.update({
                        "detected_report_family": report_type,
                        "confidence": detection.confidence if detection else 0.0,
                        "detected_version": detection.version if detection else "fallback",
                        "detection_signals": list(detection.signals) if detection else [],
                        "attempted_parsers": list(errors) + [report_type],
                    })
                    report.parsing_metadata = metadata
                    return report, report_type
                errors.append(f"{report_type}: report contained no valid tests")
            except Exception as exc:
                errors.append(f"{report_type}: {exc}")
        raise ValueError("No parser could produce a valid report. " + "; ".join(errors))
