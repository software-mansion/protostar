import re

from hypothesis import Verbosity

HYPOTHESIS_VERBOSITY = Verbosity.normal
"""
Change this value to ``Verbosity.verbose`` while debugging Hypothesis adapter code.
"""

HYPOTHESIS_MSG_JAMMER_PATTERN = re.compile(r"^Draw|^(Trying|Falsifying) example:")


def protostar_reporter(message: str):
    if (
        HYPOTHESIS_VERBOSITY > Verbosity.normal
        or not HYPOTHESIS_MSG_JAMMER_PATTERN.match(message)
    ):
        print(message)
