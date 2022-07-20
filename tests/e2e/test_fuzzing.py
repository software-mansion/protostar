import pytest


@pytest.mark.usefixtures("init")
def test_fuzzing(protostar, copy_fixture):
    copy_fixture("test_fuzz.cairo", "./tests")

    result = protostar(
        ["--no-color", "test", "tests/test_fuzz.cairo"], ignore_exit_code=True
    )

    # To keep assertions free from having to exclude trailing \n
    result += "\n"

    assert "2 failed, 1 passed, 3 total" in result

    assert "[PASS] tests/test_fuzz.cairo" in result
    assert "mean: 18, δ: 0.0, min: 18, max: 18" in result

    assert "[FAIL] tests/test_fuzz.cairo test_fails_if_big_single_input" in result
    assert (
        """
[falsifying example]:
x = 340282366920938463463374607431768211456
"""
        in result
    )

    assert "[FAIL] tests/test_fuzz.cairo test_fails_if_big_many_inputs" in result
    assert (
        """
[falsifying example]:
a = 340282366920938463463374607431768211456
b = 0
c = 0
"""
        in result
    )
