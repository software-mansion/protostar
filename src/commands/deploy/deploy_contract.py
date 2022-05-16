from pathlib import Path
from types import SimpleNamespace
from typing import Optional, Sequence

from starkware.starknet.cli.starknet_cli import deploy

from src.commands.deploy.network_config import NetworkConfig


async def deploy_contract(
    network: NetworkConfig,
    compiled_contract_path: Path,
    inputs: Optional[Sequence[str | int]] = None,
    salt: Optional[str] = None,
) -> None:
    """Version of deploy function from starkware.starknet.cli.starknet_cli independent of CLI logic."""

    args = SimpleNamespace()
    args.gateway_url = network.gateway_url
    args.network = network.starkware_network_name

    command_args = SimpleNamespace()
    command_args.inputs = inputs
    command_args.contract = str(compiled_contract_path)
    command_args.salt = salt

    await deploy(args, command_args)
