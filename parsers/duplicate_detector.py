"""Deduplication of test results produced by overlapping log entries."""

from collections import OrderedDict


class DuplicateDetector:
    """Merge duplicate tests using classname, method name and status."""

    @staticmethod
    def merge_report(report):
        classes = OrderedDict()
        seen = {}
        source_tests = [
            (class_result.name, list(class_result.tests))
            for class_result in report.classes
        ]
        for class_result in report.classes:
            target = classes.setdefault(class_result.name, class_result)
            if target is not class_result:
                target.tests.extend(class_result.tests)
        for target in classes.values():
            target.tests = []
        for class_name, tests in source_tests:
            target = classes[class_name]
            for test in tests:
                key = (test.classname, test.name, test.status)
                existing = seen.get(key)
                if existing is None:
                    seen[key] = test
                    target.tests.append(test)
                else:
                    DuplicateDetector._merge_test(existing, test)

        report.classes = list(classes.values())
        report.sort_classes()
        return report

    @staticmethod
    def _merge_test(target, duplicate):
        """Keep the richest data while preserving one model instance."""
        target.time = max(target.time, duplicate.time)
        for field in ("message", "stacktrace", "system_out", "system_err"):
            if not getattr(target, field) and getattr(duplicate, field):
                setattr(target, field, getattr(duplicate, field))
        for field in ("logs", "warnings", "errors"):
            values = getattr(target, field)
            for value in getattr(duplicate, field):
                if value not in values:
                    values.append(value)
