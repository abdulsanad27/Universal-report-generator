from dataclasses import dataclass, field
from .run_information import RunInformation
from typing import List

from .class_result import ClassResult


@dataclass
class Report:
    """
    Universal Report Model

    Every parser (XML, JSON, TXT, HTML, LOG)
    returns this object.
    """

    suite_name: str = "Unknown Test Suite"

    timestamp: str = ""

    report_type: str = ""

    # NEW
    run_information: RunInformation = field(
    default_factory=RunInformation
    )

    summary_total: int = 0
    summary_passed: int = 0
    summary_failed: int = 0
    summary_skipped: int = 0

    has_test_data: bool = False
    note: str = ""

    classes: List[ClassResult] = field(default_factory=list)

    def add_class(self, cls: ClassResult):
        self.classes.append(cls)

    @property
    def total(self):
        return self.summary_total if self.summary_total else sum(c.total for c in self.classes)

    @property
    def passed(self):
        return self.summary_passed if self.summary_passed else sum(c.passed for c in self.classes)

    @property
    def failed(self):
        return self.summary_failed if self.summary_failed else sum(c.failed for c in self.classes)

    @property
    def skipped(self):
        return self.summary_skipped if self.summary_skipped else sum(c.skipped for c in self.classes)

    @property
    def time(self):
        return round(sum(c.time for c in self.classes), 3)

    def sort_classes(self):
        """
        Failed classes first.
        """
        self.classes.sort(
            key=lambda c: (
                0 if c.failed > 0 else 1,
                c.short_name.lower()
            )
        )

    def get_failed_classes(self):
        return [
            c for c in self.classes
            if c.failed > 0
        ]

    def get_passed_classes(self):
        return [
            c for c in self.classes
            if c.failed == 0
        ]