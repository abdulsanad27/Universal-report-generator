"""Backward-compatible entry point for content-based detection."""

from .parser_detector import ParserDetector


def detect_file_type(filename: str, file_bytes: bytes) -> str:
    detections = ParserDetector().detect(file_bytes, filename)
    if not detections:
        raise ValueError("Unable to detect a supported report format from file content.")
    return detections[0].report_type
