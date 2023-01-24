from dataclasses import dataclass
from typing import Set


@dataclass
class CairoTestResultsData:
    passed: Set[str]
    failed: Set[str]
    broken: Set[str]
    skipped: Set[str]

    def __repr__(self) -> str:
        passed = "[Passed]\n" + "\n".join(sorted(self.passed))
        failed = "[Failed]\n" + "\n".join(sorted(self.failed))
        broken = "[Broken]\n" + "\n".join(sorted(self.broken))
        skipped = "[Skipped]\n" + "\n".join(sorted(self.skipped))
        return "\n".join([passed, failed, broken, skipped])
