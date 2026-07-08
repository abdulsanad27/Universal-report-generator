import re

from parsers.base_parser import BaseParser

from models.report import Report
from models.class_result import ClassResult
from models.test_result import TestResult


class HostLogParser(BaseParser):
    """
    Parses TradeFed host_log.txt and similar summary logs.
    Extracts execution metadata and summary details.
    """

    START_PATTERN = re.compile(
        r"Starting invocation",
        re.IGNORECASE
    )

    END_PATTERN = re.compile(
        r"Invocation finished|End of Results|Cleaning up builds",
        re.IGNORECASE
    )

    DEVICE_PATTERN = re.compile(
        r"device[:=]\s*(.*)",
        re.IGNORECASE
    )

    MODULE_PATTERN = re.compile(
        r"module[:=]\s*(.*)",
        re.IGNORECASE
    )

    BUILD_PATTERN = re.compile(
        r"build[:=]\s*(.*)",
        re.IGNORECASE
    )

    ERROR_PATTERN = re.compile(
        r"(ERROR|EXCEPTION|FATAL)",
        re.IGNORECASE
    )

    WARNING_PATTERN = re.compile(
        r"(WARN|WARNING)",
        re.IGNORECASE
    )

    SUMMARY_TOTAL_PATTERN = re.compile(r"Total Tests\s*:\s*(\d+)", re.IGNORECASE)
    SUMMARY_PASSED_PATTERN = re.compile(r"PASSED\s*:\s*(\d+)", re.IGNORECASE)
    SUMMARY_FAILED_PATTERN = re.compile(r"FAILED\s*:\s*(\d+)", re.IGNORECASE)
    SUMMARY_IGNORED_PATTERN = re.compile(r"IGNORED\s*:\s*(\d+)", re.IGNORECASE)
    TEST_STARTED_PATTERN = re.compile(r"ModuleListener\.testStarted\((.+?)#(.+)\)", re.IGNORECASE)
    TEST_RESULT_PATTERN = re.compile(r"\[(\d+)/(\d+)\]\s+.*?\s+(.+?)#(.+)\s+(PASSED|FAILED|SKIPPED|IGNORED)", re.IGNORECASE)
    MODULE_NAME_PATTERN = re.compile(r"([A-Za-z0-9_.-]+)\s*:\s*\d+", re.IGNORECASE)

    def parse(self, file_bytes):

        text = self.decode_file(file_bytes)

        report = Report()

        report.report_type = "tradefed_host"

        report.suite_name = "TradeFed Host Log"

        info = report.run_information

        total_tests = 0
        passed = 0
        failed = 0
        ignored = 0
        summary_class = None
        classes = {}
        current_test = None

        for line in text.splitlines():

            line = line.strip()

            if not line:
                continue

            if self.START_PATTERN.search(line):
                info.started = True

            if self.END_PATTERN.search(line):
                info.finished = True

            match = self.DEVICE_PATTERN.search(line)
            if match:
                info.device = match.group(1).strip()

            match = self.MODULE_PATTERN.search(line)
            if match:
                info.module = match.group(1).strip()

            match = self.BUILD_PATTERN.search(line)
            if match:
                info.build = match.group(1).strip()

            total_match = self.SUMMARY_TOTAL_PATTERN.search(line)
            if total_match:
                total_tests = int(total_match.group(1))
                report.summary_total = total_tests
                info.information.append(f"Total Tests: {total_tests}")

            passed_match = self.SUMMARY_PASSED_PATTERN.search(line)
            if passed_match:
                passed = int(passed_match.group(1))
                report.summary_passed = passed
                info.information.append(f"Passed: {passed}")

            failed_match = self.SUMMARY_FAILED_PATTERN.search(line)
            if failed_match:
                failed = int(failed_match.group(1))
                report.summary_failed = failed
                info.information.append(f"Failed: {failed}")

            ignored_match = self.SUMMARY_IGNORED_PATTERN.search(line)
            if ignored_match:
                ignored = int(ignored_match.group(1))
                report.summary_skipped = ignored
                info.information.append(f"Ignored: {ignored}")

            started_match = self.TEST_STARTED_PATTERN.search(line)
            if started_match:
                class_name = started_match.group(1).split('.')[-1]
                test_name = started_match.group(2)
                if class_name not in classes:
                    classes[class_name] = ClassResult(name=class_name)
                current_test = TestResult(
                    name=test_name,
                    classname=class_name,
                    status="pass",
                    time=0.0,
                    message="",
                    stacktrace=""
                )
                classes[class_name].add_test(current_test)
                continue

            result_match = self.TEST_RESULT_PATTERN.search(line)
            if result_match and current_test:
                status = result_match.group(5).lower()
                if status in ["passed", "failed", "skipped", "ignored"]:
                    current_test.status = "pass" if status == "passed" else "fail" if status == "failed" else "skip"
                    if status == "ignored":
                        current_test.status = "skip"
                    current_test.time = 0.0
                    current_test.message = line.strip()
                continue

            if self.ERROR_PATTERN.search(line):
                info.errors.append(line)

            if self.WARNING_PATTERN.search(line):
                info.warnings.append(line)

        for cls in classes.values():
            report.add_class(cls)

        if report.classes:
            report.has_test_data = True

        if total_tests or passed or failed or ignored:
            report.summary_total = total_tests
            report.summary_passed = passed
            report.summary_failed = failed
            report.summary_skipped = ignored

            summary_class = ClassResult(name="TradeFed Summary")
            summary_test = TestResult(
                name="Execution Summary",
                classname="TradeFed Summary",
                status="pass" if failed == 0 else "fail",
                time=0.0,
                message=(
                    f"Total Tests: {total_tests}\n"
                    f"Passed: {passed}\n"
                    f"Failed: {failed}\n"
                    f"Ignored: {ignored}"
                ),
                stacktrace=""
            )
            summary_class.add_test(summary_test)
            report.add_class(summary_class)

        if not report.classes:
            report.note = "This log file does not contain any parsed test-case data."
            fallback_class = ClassResult(name="TradeFed Host Log")
            fallback_test = TestResult(
                name="Execution Summary",
                classname="TradeFed Host Log",
                status="pass",
                time=0.0,
                message="No per-test data was found in this log file.",
                stacktrace=""
            )
            fallback_class.add_test(fallback_test)
            report.add_class(fallback_class)

        report.sort_classes()

        return report