from distutils.file_util import copy_file
from pathlib import Path

import pytest


@pytest.mark.usefixtures("init")
def test_deploying_contract_with_constructor(
    protostar, devnet_gateway_url, datadir: Path
):
    copy_file(
        src=str(datadir / "contract_with_constructor.cairo"), dst="./src/main.cairo"
    )
    protostar(["build"])

    result = protostar(
        [
            "--no-color",
            "deploy",
            "./build/main.json",
            "--inputs",
            "42",
            "--gateway-url",
            devnet_gateway_url,
        ]
    )

    assert "Deploy transaction was sent" in result


@pytest.mark.usefixtures("init")
def test_deploying_contract_with_constructor_and_inputs_defined_in_config_file(
    protostar, devnet_gateway_url, datadir: Path
):
    copy_file(
        src=str(datadir / "contract_with_constructor.cairo"), dst="./src/main.cairo"
    )
    copy_file(
        src=str(datadir / "protostar_toml_with_constructor_args.toml"),
        dst="./protostar.toml",
    )
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
