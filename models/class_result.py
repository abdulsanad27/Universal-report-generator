from dataclasses import dataclass, field
from typing import List

from .test_result import TestResult


@dataclass
class ClassResult:
    """
    Represents one Java/Kotlin test class.
    """

    name: str

    tests: List[TestResult] = field(default_factory=list)

    @property
    def short_name(self):
        return self.name.split(".")[-1]

    @property
    def total(self):
        return len(self.tests)

    @property
    def passed(self):
        return sum(1 for t in self.tests if t.status == "pass")

    @property
    def failed(self):
        return sum(1 for t in self.tests if t.status == "fail")

    @property
    def skipped(self):
        return sum(1 for t in self.tests if t.status == "skip")

    @property
    def time(self):
        return round(sum(t.time for t in self.tests), 3)

    @property
    def has_failures(self):
        return self.failed > 0

    @property
    def has_warnings(self):
        return any(t.warnings for t in self.tests)

    @property
    def has_errors(self):
        return any(t.errors for t in self.tests)

    @property
    def total_logs(self):
        return sum(len(t.logs) for t in self.tests)

    def add_test(self, test: TestResult):
        self.tests.append(test)