import os


class Config:
    """
    Application Configuration
    """

    # -------------------------------------------------
    # Project Root
    # -------------------------------------------------

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # -------------------------------------------------
    # Upload Folder
    # -------------------------------------------------

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

    # -------------------------------------------------
    # Flask Settings
    # -------------------------------------------------

    SECRET_KEY = "UniversalReportAnalyzer2026"

    DEBUG = True

    # -------------------------------------------------
    # Maximum Upload Size
    # -------------------------------------------------

    MAX_CONTENT_LENGTH = 20 * 1024 * 1024      # 20 MB

    # -------------------------------------------------
    # Supported Extensions
    # -------------------------------------------------

    ALLOWED_EXTENSIONS = {
        "xml",
        "json",
        "txt",
        "log",
        "html",
        "htm"
    }

    # -------------------------------------------------
    # Report Types
    # -------------------------------------------------

    REPORT_TYPES = {
        "XML": "xml",
        "JSON": "json",
        "TXT": "txt",
        "LOG": "log",
        "HTML": "html"
    }

    # -------------------------------------------------
    # Supported MIME Types
    # -------------------------------------------------

    MIME_TYPES = {

        "application/xml": "xml",

        "text/xml": "xml",

        "application/json": "json",

        "text/plain": "txt",

        "text/html": "html"
    }

    # -------------------------------------------------
    # HTML Report Settings
    # -------------------------------------------------

    APP_NAME = "Universal Test Report Analyzer"

    VERSION = "2.0"

    DEFAULT_SUITE_NAME = "Unknown Test Suite"

    DEFAULT_TIMESTAMP = "-"

    SHOW_STACK_TRACE = True

    SHOW_FAILURE_MESSAGE = True

    GROUP_BY_CLASS = True

    ENABLE_SEARCH = True

    ENABLE_FILTER = True

    ENABLE_COLLAPSE = True

    ENABLE_STATISTICS = True

    ENABLE_UPLOAD_PAGE = True

    # -------------------------------------------------
    # Test Status Colors
    # -------------------------------------------------

    STATUS_COLORS = {
        "pass": "#3fb950",
        "fail": "#f85149",
        "skip": "#d29922",
        "unknown": "#8b949e"
    }

    # -------------------------------------------------
    # Icons
    # -------------------------------------------------

    STATUS_ICONS = {
        "pass": "✔",
        "fail": "✖",
        "skip": "➜",
        "unknown": "?"
    }

    # -------------------------------------------------
    # Supported Report Names
    # -------------------------------------------------

    XML_SIGNATURES = [
        "<?xml",
        "<testsuite",
        "<testsuites"
    ]

    JSON_SIGNATURES = [
        "{",
        "["
    ]

    HTML_SIGNATURES = [
        "<html",
        "<!DOCTYPE html"
    ]

    LOG_KEYWORDS = [
        "FAIL",
        "FAILED",
        "PASS",
        "PASSED",
        "ERROR",
        "EXCEPTION",
        "STACKTRACE",
        "TEST"
    ]

    TXT_KEYWORDS = [
        "PASS",
        "FAIL",
        "SKIP"
    ]