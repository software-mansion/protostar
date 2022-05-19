import pytest


@pytest.mark.usefixtures("init")
def test_deploying_basic_example(protostar):
    protostar(["build"])

    result = protostar(["deploy", "./build/main.json", "--network", "alpha-goerli"])

    assert "Deploy transaction was sent" in result
