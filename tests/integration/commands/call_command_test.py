import json
from pathlib import Path

import pytest
from protostar.protostar_exception import ProtostarException
from tests._conftest.devnet.devnet_fixture import DevnetFixture
from tests.conftest import DevnetAccount, SetPrivateKeyEnvVarFixture
from tests.data.contracts import UINT256_IDENTITY_CONTRACT
from tests.integration.conftest import CreateProtostarProjectFixture
from tests.integration._conftest import ProtostarFixture, ProtostarProjectFixture


@pytest.fixture(name="protostar_project")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar_project:
        protostar_project.create_files(
            {"src/main.cairo": Path(__file__).parent / "getter_contract.cairo"}
        )
        protostar_project.protostar.build_cairo0_sync()
        yield protostar_project


async def test_call(
    protostar_project: ProtostarProjectFixture,
    devnet_gateway_url: str,
    devnet_account: DevnetAccount,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
):
    with set_private_key_env_var(devnet_account.private_key):
        declare_response = await protostar_project.protostar.declare(
            contract=protostar_project.protostar.project_root_path
            / "build"
            / "main.json",
            gateway_url=devnet_gateway_url,
            account_address=devnet_account.address,
            max_fee="auto",
        )
        deploy_response = await protostar_project.protostar.deploy(
            class_hash=declare_response.class_hash,
            gateway_url=devnet_gateway_url,
            account_address=devnet_account.address,
            max_fee="auto",
        )

    result = await protostar_project.protostar.call(
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
    protostar_project: ProtostarProjectFixture,
    devnet_gateway_url: str,
    devnet_account: DevnetAccount,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
):
    with set_private_key_env_var(devnet_account.private_key):
        deploy_response = await deploy_main_contract(
            protostar_project.protostar, devnet_gateway_url, devnet_account
        )

    result = await protostar_project.protostar.call(
        contract_address=deploy_response.address,
        function_name="add_multiple_values",
        inputs=[3, 2, 5],
        gateway_url=devnet_gateway_url,
    )

    assert result.call_output.cairo_data == [10]


async def test_call_inputs_args_dict(
    protostar_project: ProtostarProjectFixture,
    devnet_gateway_url: str,
    devnet_account: DevnetAccount,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
):
    with set_private_key_env_var(devnet_account.private_key):
        deploy_response = await deploy_main_contract(
            protostar_project.protostar, devnet_gateway_url, devnet_account
        )

    result = await protostar_project.protostar.call(
        contract_address=deploy_response.address,
        function_name="add_multiple_values",
        inputs={"a": 5, "c": 3, "b": 2},
        gateway_url=devnet_gateway_url,
    )

    assert result.call_output.cairo_data == [10]


async def test_call_inputs_args_dict_with_custom_abi(
    protostar_project: ProtostarProjectFixture,
    devnet_gateway_url: str,
    devnet_account: DevnetAccount,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
):
    with set_private_key_env_var(devnet_account.private_key):
        deploy_response = await deploy_main_contract(
            protostar_project.protostar, devnet_gateway_url, devnet_account
        )

    result = await protostar_project.protostar.call(
        contract_address=deploy_response.address,
        function_name="add_multiple_values",
        inputs={"a": 5, "c": 3, "b": 2},
        gateway_url=devnet_gateway_url,
        abi_path=protostar_project.protostar.project_root_path
        / "build"
        / "main_abi.json",
    )

    assert result.call_output.cairo_data == [10]


async def test_error_when_custom_abi_is_invalid(
    protostar_project: ProtostarProjectFixture,
    devnet_gateway_url: str,
    devnet_account: DevnetAccount,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
):
    with set_private_key_env_var(devnet_account.private_key):
        deploy_response = await deploy_main_contract(
            protostar_project.protostar, devnet_gateway_url, devnet_account
        )

    with pytest.raises(ProtostarException):
        await protostar_project.protostar.call(
            contract_address=deploy_response.address,
            function_name="add_multiple_values",
            inputs={"a": 5, "c": 3, "b": 2},
            gateway_url=devnet_gateway_url,
            abi_path=protostar_project.protostar.project_root_path
            / "build"
            / "main.json",
        )


async def test_call_inputs_args_dict_fail(
    protostar_project: ProtostarProjectFixture,
    devnet_gateway_url: str,
    devnet_account: DevnetAccount,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
):
    with set_private_key_env_var(devnet_account.private_key):
        deploy_response = await deploy_main_contract(
            protostar_project.protostar, devnet_gateway_url, devnet_account
        )

    with pytest.raises(ProtostarException):
        await protostar_project.protostar.call(
            contract_address=deploy_response.address,
            function_name="add_multiple_values",
            inputs={"a": 5, "c": 3, "ba": 2},
            gateway_url=devnet_gateway_url,
        )


async def test_call_failure(
    protostar_project: ProtostarProjectFixture,
    devnet_gateway_url: str,
    devnet_account: DevnetAccount,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
):
    await protostar_project.protostar.build_cairo0()
    with set_private_key_env_var(devnet_account.private_key):
        declare_response = await protostar_project.protostar.declare(
            protostar_project.protostar.project_root_path / "build" / "main.json",
            gateway_url=devnet_gateway_url,
            account_address=devnet_account.address,
            max_fee="auto",
        )
        deploy_response = await protostar_project.protostar.deploy(
            class_hash=declare_response.class_hash,
            gateway_url=devnet_gateway_url,
            account_address=devnet_account.address,
            max_fee="auto",
        )

    with pytest.raises(ProtostarException, match="0 != 1"):
        await protostar_project.protostar.call(
            contract_address=deploy_response.address,
            function_name="error_call",
            inputs=[],
            gateway_url=devnet_gateway_url,
        )


async def test_uint256(
    protostar_project: ProtostarProjectFixture,
    devnet_gateway_url: str,
    devnet_account: DevnetAccount,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
    capsys: pytest.CaptureFixture[str],
):
    protostar_project.create_files({"./src/main.cairo": UINT256_IDENTITY_CONTRACT})
    await protostar_project.protostar.build_cairo0()
    with set_private_key_env_var(devnet_account.private_key):
        declare_response = await protostar_project.protostar.declare(
            contract=protostar_project.protostar.project_root_path
            / "build"
            / "main.json",
            gateway_url=devnet_gateway_url,
            max_fee="auto",
            account_address=devnet_account.address,
        )
        deploy_response = await protostar_project.protostar.deploy(
            class_hash=declare_response.class_hash,
            gateway_url=devnet_gateway_url,
            max_fee="auto",
            account_address=devnet_account.address,
        )

        capsys.readouterr()
        await protostar_project.protostar.call(
            contract_address=deploy_response.address,
            function_name="identity",
            inputs=[21, 37],
            gateway_url=devnet_gateway_url,
        )
        logged_result = capsys.readouterr().out

        assert "[21, 37]" in logged_result
        assert '"res": 12590447576074723148144860474975423823893' in logged_result


async def test_json(
    protostar_project: ProtostarProjectFixture,
    devnet_gateway_url: str,
    devnet_account: DevnetAccount,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
    capsys: pytest.CaptureFixture[str],
):
    protostar_project.create_files({"./src/main.cairo": UINT256_IDENTITY_CONTRACT})
    await protostar_project.protostar.build_cairo0()
    with set_private_key_env_var(devnet_account.private_key):
        declare_response = await protostar_project.protostar.declare(
            contract=protostar_project.protostar.project_root_path
            / "build"
            / "main.json",
            gateway_url=devnet_gateway_url,
            max_fee="auto",
            account_address=devnet_account.address,
        )
        deploy_response = await protostar_project.protostar.deploy(
            class_hash=declare_response.class_hash,
            gateway_url=devnet_gateway_url,
            max_fee="auto",
            account_address=devnet_account.address,
        )

        capsys.readouterr()
        await protostar_project.protostar.call(
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
    protostar_project: ProtostarProjectFixture,
    devnet: DevnetFixture,
    devnet_account: DevnetAccount,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
):
    with set_private_key_env_var(devnet_account.private_key):
        declared = await protostar_project.protostar.declare(
            contract=protostar_project.protostar.project_root_path
            / "build"
            / "main.json",
            gateway_url=devnet.get_gateway_url(),
            max_fee="auto",
            account_address=devnet_account.address,
            wait_for_acceptance=True,
        )
        contract_abi_path = (
            protostar_project.protostar.project_root_path / "build" / "main_abi.json"
        )

        protostar_project.create_contracts(
            {"proxy": Path(__file__).parent / "proxy.cairo"}
        )
        await protostar_project.protostar.build_cairo0()

        declared_proxy = await protostar_project.protostar.declare(
            contract=protostar_project.protostar.project_root_path
            / "build"
            / "proxy.json",
            wait_for_acceptance=True,
            account_address=devnet_account.address,
            gateway_url=devnet.get_gateway_url(),
            max_fee="auto",
        )

        proxy = await protostar_project.protostar.deploy(
            class_hash=declared_proxy.class_hash,
            inputs=[
                int(declared.class_hash),
                0,
                0,
            ],  # See @constructor signature at proxy.cairo
            account_address=devnet_account.address,
            max_fee="auto",
            gateway_url=devnet.get_gateway_url(),
            wait_for_acceptance=True,
        )

        call_result = await protostar_project.protostar.call(
            contract_address=proxy.address,
            gateway_url=devnet.get_gateway_url(),
            function_name="add_multiple_values",
            inputs={"a": 1, "b": 2, "c": 3},
            abi_path=contract_abi_path,
        )

    assert call_result.call_output.human_data is not None
    assert call_result.call_output.human_data["res"] == 6
