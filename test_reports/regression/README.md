# Android Automotive parser regression pack

These are deliberately realistic, adversarial fixtures—not simplified parser
examples. Keep them immutable once a parser behaviour is approved. Add a new
fixture rather than weakening an existing expected outcome.

`manifest.json` identifies the expected report family, the minimum recovered
tests, and the scenarios exercised. Counts exclude host-log summary metadata.
Malformed files specify the minimum data that should survive recovery.

The `stress_tradefed_host.log` fixture contains repeated module/retry output and
mixed outcomes. It is intentionally line-oriented so it can be expanded without
altering its structural patterns.
