from pathlib import Path


# Warning! When updating number of tests run - this measure threshold has to be updated
ROUNDS_NUMBER = 15  # Times each function is expected to run
THRESHOLD = 2.145  # A measure which each function run must not exceed
BENCHMARKS_PATH = Path(__file__).parent.parent.parent / ".benchmarks"
