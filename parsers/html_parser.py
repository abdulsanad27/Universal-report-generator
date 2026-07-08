from bs4 import BeautifulSoup

from .base_parser import BaseParser

from models.report import Report
from models.class_result import ClassResult
from models.test_result import TestResult


class HtmlParser(BaseParser):

    def parse(self, file_bytes):

        html = self.decode_file(file_bytes)

        soup = BeautifulSoup(html, "html.parser")

        report = Report()

        report.report_type = "html"

        report.suite_name = "HTML Test Report"

        report.timestamp = ""

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

                status = None

                if "pass" in text:
                    status = "pass"

                elif "fail" in text:
                    status = "fail"

                elif "skip" in text:
                    status = "skip"

                if status is None:
                    continue

                name = values[1] if len(values) > 1 else "Unknown Test"

                execution_time = 0

                if len(values) >= 3:

                    try:
                        execution_time = float(values[2])
                    except:
                        execution_time = 0

                message = ""

                if len(values) >= 4:
                    message = values[3]

                test = TestResult(

                    name=name,

                    classname=current_class.name,

                    status=status,

                    time=execution_time,

                    message=message,

                    stacktrace=message

                )

                current_class.add_test(test)

        report.add_class(current_class)

        report.sort_classes()

        return report