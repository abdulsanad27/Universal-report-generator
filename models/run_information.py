from dataclasses import dataclass, field
from typing import List


@dataclass
class RunInformation:
    """
    Stores execution information about a test run.

    This information is independent of the individual
    test results.
    """

    device: str = ""

    module: str = ""

    build: str = ""

    branch: str = ""

    suite: str = ""

    command: str = ""

    started: bool = False

    finished: bool = False

    start_time: str = ""

    end_time: str = ""

    duration: str = ""

    errors: List[str] = field(default_factory=list)

    warnings: List[str] = field(default_factory=list)

    information: List[str] = field(default_factory=list)