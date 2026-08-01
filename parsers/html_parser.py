from bs4 import BeautifulSoup

from .base_parser import BaseParser

from models.report import Report
from models.class_result import ClassResult
from models.test_result import TestResult


class HtmlParser(BaseParser):

    def parse(self, file_bytes):

        html = self.decode_file(file_bytes)

        soup = BeautifulSoup(html, "html.parser")

        report = self.create_report("html", "HTML Test Report")

        current_class = ClassResult(
            name="HTML Report"
        )

        tables = soup.find_all("table")

        if not tables:
            raise Exception(
                "No table found inside HTML report."
            )

        for table in tables:

            rows = table.find_all("tr")

            for row in rows:

                cols = row.find_all(["td", "th"])

                if len(cols) < 2:
                    continue

                values = [
                    c.get_text(strip=True)
                    for c in cols
                ]

                text = " ".join(values).lower()

                raw_status = next((value for value in values if value.upper() in {
                    "PASS", "PASSED", "SUCCESS", "OK", "TRUE", "FAIL", "FAILED", "FAILURE",
                    "ERROR", "EXCEPTION", "ASSERTION", "TIMEOUT", "ABORTED",
                    "SKIP", "SKIPPED", "IGNORED", "DISABLED", "NOTRUN"}), None)
                if raw_status is None:
                    continue
                status = self.normalize_status(raw_status)

                name = values[1] if len(values) > 1 else "Unknown Test"

                execution_time = 0

                if len(values) >= 3:

                    execution_time = self.safe_float(values[2])

                message = ""

                if len(values) >= 4:
                    message = values[3]

                test = self.create_test(name, current_class.name, status, execution_time,
                                        message=message, stacktrace=message)

                current_class.add_test(test)

        report.add_class(current_class)

        return self.finalize_report(report)
