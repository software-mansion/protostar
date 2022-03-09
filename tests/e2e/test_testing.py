import pytest


@pytest.mark.usefixtures("init")
def test_basic_contract(protostar):
    result = protostar(["test", "tests"])
    assert result == "No cases found"
