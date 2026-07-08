from dataclasses import dataclass, field
from typing import List


@dataclass
class TestResult:
    """
    Represents one test method.
    """

    # -----------------------------
    # Basic Information
    # -----------------------------

    name: str

    classname: str

    status: str = "pass"

    time: float = 0.0

    # -----------------------------
    # Failure Information
    # -----------------------------

    message: str = ""

    stacktrace: str = ""

    # -----------------------------
    # Console Output
    # -----------------------------

    system_out: str = ""

    system_err: str = ""

    # -----------------------------
    # TradeFed / Robolectric Logs
    # -----------------------------

    logs: List[str] = field(default_factory=list)

    warnings: List[str] = field(default_factory=list)

    errors: List[str] = field(default_factory=list)

    # -----------------------------
    # Helper Functions
    # -----------------------------

    def is_pass(self):
        return self.status == "pass"

    def is_fail(self):
        return self.status == "fail"

    def is_skip(self):
        return self.status == "skip"

    def add_log(self, line: str):
        self.logs.append(line)

    def add_warning(self, line: str):
        self.warnings.append(line)

    def add_error(self, line: str):
        self.errors.append(line)