"""Canonical status handling for every supported report format."""


class StatusNormalizer:
    """Maps vendor-specific result words to the three supported outcomes."""

    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"

    _MAPPING = {
        "PASS": PASS, "PASSED": PASS, "SUCCESS": PASS, "OK": PASS,
        "TRUE": PASS, "COMPLETED": PASS, "RUN": PASS,
        "FAIL": FAIL, "FAILED": FAIL, "FAILURE": FAIL, "ERROR": FAIL,
        "EXCEPTION": FAIL, "ASSERTION": FAIL, "ASSERTIONERROR": FAIL,
        "TIMEOUT": FAIL, "ABORTED": FAIL, "FATAL": FAIL,
        "SKIP": SKIP, "SKIPPED": SKIP, "IGNORED": SKIP,
        "DISABLED": SKIP, "NOTRUN": SKIP, "NOT_RUN": SKIP,
    }

    @classmethod
    def configure(cls, aliases):
        """Register future/vendor aliases without editing parser code.

        ``aliases`` maps an alias to PASS, FAIL or SKIP. Invalid mappings are
        rejected early so every parser retains the same three-state contract.
        """
        for alias, status in aliases.items():
            canonical = str(status).upper()
            if canonical not in {cls.PASS, cls.FAIL, cls.SKIP}:
                raise ValueError("Status aliases must map to PASS, FAIL, or SKIP.")
            cls._MAPPING[str(alias).strip().upper()] = canonical

    @classmethod
    def normalize(cls, value, default=SKIP):
        """Return ``PASS``, ``FAIL`` or ``SKIP`` for *value*.

        Unknown or missing values are deliberately treated as skipped.  This is
        safer than reporting an unrecognised outcome as a passing test.
        """
        if value is None:
            return default
        key = str(value).strip().upper().replace(" ", "_")
        return cls._MAPPING.get(key, default)
