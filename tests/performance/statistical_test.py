import json
import math
from glob import glob

from tests.performance.constants import ROUNDS_NUMBER, THRESHOLD, BENCHMARKS_PATH


def get_benchmarks():
    benchmarks = []
    for benchmark_path in glob(f"{BENCHMARKS_PATH}/**/*.json"):
        with open(benchmark_path, mode="r", encoding="utf-8") as file:
            contents = json.load(file)
            benchmarks.append(contents)
    return benchmarks


def find_test(benchmarks, test_name):
    for benchmark in benchmarks:
        if benchmark["name"] == test_name:
            return benchmark
    raise RuntimeError(
        f"Did not find matching {test_name} test in the second benchmark. "
        f"Perhaps it was removed - in which case you need to re-generate baseline file."
    )


def calc_t_student_measure(before, after):
    before_stats = before["stats"]
    after_stats = after["stats"]
    mean_before = before_stats["mean"]
    mean_after = after_stats["mean"]
    n_before = before_stats["iterations"] * before_stats["rounds"]
    n_after = after_stats["iterations"] * after_stats["rounds"]

    variance_before = before_stats["stddev"] ** 2
    variance_after = after_stats["stddev"] ** 2

    return (mean_before - mean_after) / math.sqrt(
        (
            ((n_before * variance_before) + (n_after * variance_after))
            / (n_before + n_after - 2)
        )
        * ((1 / n_before) + (1 / n_after))
    )


def extract_measure(before, after, test_name):
    before_test = find_test(before["benchmarks"], test_name)
    after_test = find_test(after["benchmarks"], test_name)
    return calc_t_student_measure(before_test, after_test)


def assert_benchmark_runs_matches_config(run):
    for benchmark in run["benchmarks"]:
        times_run = benchmark["stats"]["rounds"] * benchmark["stats"]["iterations"]
        assert (
            times_run == n
        ), f"Number of tests run in {benchmark['name']} is not correct ({times_run} instead of {n})!"


def main():
    benchmarks = get_benchmarks()
    assert len(benchmarks) == 2, "There are more than 2 benchmarks to compare"
    # We assume they were sorted by lex order
    before, after = benchmarks
    for test in before["benchmarks"]:
        measure = extract_measure(before, after, test["name"])
        assert_n(after, ROUNDS_NUMBER)
        assert_n(before, ROUNDS_NUMBER)
        assert (
            abs(measure) <= THRESHOLD
        ), f"Measure exceeds given threshold ({abs(measure)} >= {THRESHOLD})"
    print("Performance assessment: not degraded")


if __name__ == "__main__":
    main()
