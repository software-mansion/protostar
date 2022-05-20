import pytest


@pytest.mark.usefixtures("init")
def test_deploying_basic_example_to_devnet(protostar, devnet_gateway_url):
    protostar(["build"])

    result = protostar(
        [
            "--no-color",
            "deploy",
            "./build/main.json",
            "--gateway-url",
            devnet_gateway_url,
        ]
    )

    assert "Deploy transaction was sent" in result
