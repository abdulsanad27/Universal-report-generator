import re


def detect_file_type(filename: str, file_bytes: bytes) -> str:
    """
    Detect report type using filename and content.
    """

    filename = filename.lower()

    try:
        text = file_bytes.decode("utf-8", errors="ignore")
    except Exception:
        text = ""

    # ---------------------------------------------------------
    # XML
    # ---------------------------------------------------------

    if filename.endswith(".xml"):

        if "<testsuite" in text or "<testsuites" in text:
            return "xml"

        # Treat TradeFed XML configuration files as their own parser type.
        return "tradefed_config"

    # ---------------------------------------------------------
    # JSON
    # ---------------------------------------------------------

    if filename.endswith(".json"):
        return "json"

    # ---------------------------------------------------------
    # HTML
    # ---------------------------------------------------------

    if filename.endswith(".html") or filename.endswith(".htm"):
        return "html"

    # ---------------------------------------------------------
    # TXT / LOG
    # ---------------------------------------------------------

    if filename.endswith(".txt") or filename.endswith(".log"):

        #
        # TradeFed Event Log
        #

        if "- test:" in text and "(status=" in text:
            return "tradefed_event"

        #
        # Java Log
        #

        if (
            "Starting class:" in text
            or "[Robolectric]" in text
            or "Done executing class" in text
        ):
            return "tradefed_java"

        #
        # Passed Tests
        #

        if (
            "CeerCarSettingsRoboTests" in text
            and "#" in text
            and "Starting invocation" not in text
            and "Invocation finished" not in text
            and "I/TestInvocation" not in text
            and "Total Tests" not in text
            and "PASSED" not in text
            and "FAILED" not in text
            and "IGNORED" not in text
        ):
            return "tradefed_passed"

        #
        # Host Log / Summary Log
        #

        if (
            "Starting invocation" in text
            or "Invocation finished" in text
            or "I/TestInvocation" in text
            or "Total Tests" in text
            or "PASSED" in text
            or "FAILED" in text
            or "IGNORED" in text
            or "Results" in text
        ):
            return "tradefed_host"

        #
        # Generic
        #

        return "generic_txt"

    raise Exception("Unsupported report type.")