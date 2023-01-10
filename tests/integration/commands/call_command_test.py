import json
from pathlib import Path

import pytest

from protostar.protostar_exception import ProtostarException
from tests._conftest.devnet.devnet_fixture import DevnetFixture
from tests.conftest import TESTS_ROOT_PATH, DevnetAccount, SetPrivateKeyEnvVarFixture
from tests.data.contracts import UINT256_IDENTITY_CONTRACT
from tests.integration.conftest import CreateProtostarProjectFixture
from tests.integration.protostar_fixture import ProtostarFixture


@pytest.fixture(name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        protostar.create_files(
            {"src/main.cairo": Path(__file__).parent / "getter_contract.cairo"}
        )
        protostar.build_sync()
        yield protostar


async def test_call(
    protostar: ProtostarFixture,
    devnet_gateway_url: str,
    devnet_account: DevnetAccount,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
):
    with set_private_key_env_var(devnet_account.private_key):
        declare_response = await protostar.declare(
            contract=protostar.project_root_path / "build" / "main.json",
            gateway_url=devnet_gateway_url,
            account_address=devnet_account.address,
            max_fee="auto",
        )
        deploy_response = await protostar.deploy(
            class_hash=declare_response.class_hash,
            gateway_url=devnet_gateway_url,
            account_address=devnet_account.address,
            max_fee="auto",
        )

    result = await protostar.call(
        contract_address=deploy_response.address,
        function_name="add_3",
        inputs=[3],
        gateway_url=devnet_gateway_url,
    )

    assert result.call_output.cairo_data == [6]
    assert result.call_output.human_data is not None
    assert result.call_output.human_data["res"] == 6


async def deploy_main_contract(
    protostar: ProtostarFixture, devnet_gateway_url: str, devnet_account: DevnetAccount
):
    declare_response = await protostar.declare(
        contract=protostar.project_root_path / "build" / "main.json",
        gateway_url=devnet_gateway_url,
        account_address=devnet_account.address,
        max_fee="auto",
    )
    return await protostar.deploy(
        class_hash=declare_response.class_hash,
        gateway_url=devnet_gateway_url,
        account_address=devnet_account.address,
        max_fee="auto",
    )


async def test_call_inputs(
    protostar: ProtostarFixture,
    devnet_gateway_url: str,
    devnet_account: DevnetAccount,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
):
    with set_private_key_env_var(devnet_account.private_key):
        deploy_response = await deploy_main_contract(
            protostar, devnet_gateway_url, devnet_account
        )

    result = await protostar.call(
        contract_address=deploy_response.address,
        function_name="add_multiple_values",
        inputs=[3, 2, 5],
        gateway_url=devnet_gateway_url,
    )

    assert result.call_output.cairo_data == [10]


async def test_call_inputs_args_dict(
    protostar: ProtostarFixture,
    devnet_gateway_url: str,
    devnet_account: DevnetAccount,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
):
    with set_private_key_env_var(devnet_account.private_key):
        deploy_response = await deploy_main_contract(
            protostar, devnet_gateway_url, devnet_account
        )

    result = await protostar.call(
        contract_address=deploy_response.address,
        function_name="add_multiple_values",
        inputs={"a": 5, "c": 3, "b": 2},
        gateway_url=devnet_gateway_url,
    )

    assert result.call_output.cairo_data == [10]


async def test_call_inputs_args_dict_fail(
    protostar: ProtostarFixture,
    devnet_gateway_url: str,
    devnet_account: DevnetAccount,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
):
    with set_private_key_env_var(devnet_account.private_key):
        deploy_response = await deploy_main_contract(
            protostar, devnet_gateway_url, devnet_account
        )

    with pytest.raises(ProtostarException):
        await protostar.call(
            contract_address=deploy_response.address,
            function_name="add_multiple_values",
            inputs={"a": 5, "c": 3, "ba": 2},
            gateway_url=devnet_gateway_url,
        )


async def test_call_failure(
    protostar: ProtostarFixture,
    devnet_gateway_url: str,
    devnet_account: DevnetAccount,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
):
    await protostar.build()
    with set_private_key_env_var(devnet_account.private_key):
        declare_response = await protostar.declare(
            protostar.project_root_path / "build" / "main.json",
            gateway_url=devnet_gateway_url,
            account_address=devnet_account.address,
            max_fee="auto",
        )
        deploy_response = await protostar.deploy(
            class_hash=declare_response.class_hash,
            gateway_url=devnet_gateway_url,
            account_address=devnet_account.address,
            max_fee="auto",
        )

    with pytest.raises(ProtostarException, match="0 != 1"):
        await protostar.call(
            contract_address=deploy_response.address,
            function_name="error_call",
            inputs=[],
            gateway_url=devnet_gateway_url,
        )


async def test_uint256(
    protostar: ProtostarFixture,
    devnet_gateway_url: str,
    devnet_account: DevnetAccount,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
    capsys: pytest.CaptureFixture[str],
):
    protostar.create_files({"./src/main.cairo": UINT256_IDENTITY_CONTRACT})
    await protostar.build()
    with set_private_key_env_var(devnet_account.private_key):
        declare_response = await protostar.declare(
            contract=protostar.project_root_path / "build" / "main.json",
            gateway_url=devnet_gateway_url,
            max_fee="auto",
            account_address=devnet_account.address,
        )
        deploy_response = await protostar.deploy(
            class_hash=declare_response.class_hash,
            gateway_url=devnet_gateway_url,
            max_fee="auto",
            account_address=devnet_account.address,
        )

        capsys.readouterr()
        await protostar.call(
            contract_address=deploy_response.address,
            function_name="identity",
            inputs=[21, 37],
            gateway_url=devnet_gateway_url,
        )
        logged_result = capsys.readouterr().out

        assert "[21, 37]" in logged_result
        assert '"res": 12590447576074723148144860474975423823893' in logged_result


async def test_json(
    protostar: ProtostarFixture,
    devnet_gateway_url: str,
    devnet_account: DevnetAccount,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
    capsys: pytest.CaptureFixture[str],
):
    protostar.create_files({"./src/main.cairo": UINT256_IDENTITY_CONTRACT})
    await protostar.build()
    with set_private_key_env_var(devnet_account.private_key):
        declare_response = await protostar.declare(
            contract=protostar.project_root_path / "build" / "main.json",
            gateway_url=devnet_gateway_url,
            max_fee="auto",
            account_address=devnet_account.address,
        )
        deploy_response = await protostar.deploy(
            class_hash=declare_response.class_hash,
            gateway_url=devnet_gateway_url,
            max_fee="auto",
            account_address=devnet_account.address,
        )

        capsys.readouterr()
        await protostar.call(
            contract_address=deploy_response.address,
            function_name="identity",
            inputs={"arg": {"low": 21, "high": 37}},
            gateway_url=devnet_gateway_url,
            json=True,
        )
        logged_result = capsys.readouterr().out

    result = json.loads(logged_result)
    assert result["raw_output"] == [21, 37]
    assert (
        result["transformed_output"]["res"] == 12590447576074723148144860474975423823893
    )


async def test_calling_through_proxy(
    protostar: ProtostarFixture,
    devnet: DevnetFixture,
    devnet_account: DevnetAccount,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
):
    with set_private_key_env_var(devnet_account.private_key):
        declared = await protostar.declare(
            contract=protostar.project_root_path / "build" / "main.json",
            gateway_url=devnet.get_gateway_url(),
            max_fee="auto",
            account_address=devnet_account.address,
        )
        contract = await protostar.deploy(
            class_hash=declared.class_hash,
            account_address=devnet_account.address,
            max_fee="auto",
            gateway_url=devnet.get_gateway_url(),
            wait_for_acceptance=True,
        )
        declared_proxy = await protostar.declare(
            contract=TESTS_ROOT_PATH / "data" / "oz_proxy_compiled_contract.json",
            wait_for_acceptance=True,
            account_address=devnet_account.address,
            gateway_url=devnet.get_gateway_url(),
            max_fee="auto",
        )
        proxy = await protostar.deploy(
            class_hash=declared_proxy.class_hash,
            inputs=[int(contract.address)],
            account_address=devnet_account.address,
            max_fee="auto",
            gateway_url=devnet.get_gateway_url(),
            wait_for_acceptance=True,
        )

        call_result = await protostar.call(
            contract_address=proxy.address,
            gateway_url=devnet.get_gateway_url(),
            function_name="add_multiple_values",
            inputs={"a": 1, "b": 2, "c": 3},
        )

    assert call_result.call_output.human_data is not None
    assert call_result.call_output.human_data["res"] == 6
