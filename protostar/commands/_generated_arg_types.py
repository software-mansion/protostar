from dataclasses import dataclass
from typing import Optional
from ._types_for_generated_arg_types import *

@dataclass
class BuildCommandArgs:
    cairo_path: Optional[list[directory]]
    disable_hint_validation: bool = False
    compiled_contracts_dir: path = 'build'

@dataclass
class CairoMigrateCommandArgs:
    targets: list[str] = ['.']

@dataclass
class CallCommandArgs:
    contract_address: address
    function: str
    gateway_url: Optional[str]
    chain_id: Optional[int]
    network: Optional[str]
    inputs: Optional[list[felt]]

@dataclass
class DeclareCommandArgs:
    contract: path
    account_address: Optional[address]
    private_key_path: Optional[path]
    signer_class: Optional[str]
    gateway_url: Optional[str]
    chain_id: Optional[int]
    network: Optional[str]
    token: Optional[str]
    max_fee: Optional[fee]
    wait_for_acceptance: bool = False

@dataclass
class DeployCommandArgs:
    contract: path
    inputs: Optional[list[felt]]
    token: Optional[str]
    salt: Optional[felt]
    gateway_url: Optional[str]
    chain_id: Optional[int]
    network: Optional[str]
    wait_for_acceptance: bool = False

@dataclass
class DeployAccountCommandArgs:
    account_class_hash: class_hash
    max_fee: wei
    account_address_salt: int
    gateway_url: Optional[str]
    chain_id: Optional[int]
    network: Optional[str]
    account_address: Optional[address]
    private_key_path: Optional[path]
    signer_class: Optional[str]
    account_constructor_input: Optional[list[int]]
    nonce: int = 0

@dataclass
class FormatCommandArgs:
    target: list[str] = ['.']
    check: bool = False
    verbose: bool = False
    ignore_broken: bool = False

@dataclass
class InitCommandArgs:
    name: Optional[str]
    existing: bool = False

@dataclass
class InstallCommandArgs:
    lib_path: Optional[path]
    package: Optional[str]
    name: Optional[str]

@dataclass
class InvokeCommandArgs:
    contract_address: address
    function: str
    account_address: Optional[address]
    private_key_path: Optional[path]
    signer_class: Optional[str]
    gateway_url: Optional[str]
    chain_id: Optional[int]
    network: Optional[str]
    inputs: Optional[list[felt]]
    max_fee: Optional[fee]
    wait_for_acceptance: bool = False

@dataclass
class MigrateCommandArgs:
    path: path
    gateway_url: Optional[str]
    chain_id: Optional[int]
    network: Optional[str]
    account_address: Optional[address]
    private_key_path: Optional[path]
    signer_class: Optional[str]
    no_confirm: bool = False
    compiled_contracts_dir: path = 'build'

@dataclass
class MigrateConfigurationFileCommandArgs:
    pass

@dataclass
class RemoveCommandArgs:
    package: str
    lib_path: Optional[path]

@dataclass
class TestCommandArgs:
    ignore: Optional[list[str]]
    cairo_path: Optional[list[directory]]
    seed: Optional[int]
    target: list[str] = ['.']
    disable_hint_validation: bool = False
    profiling: bool = False
    no_progress_bar: bool = False
    safe_collecting: bool = False
    exit_first: bool = False
    report_slowest_tests: int = 0
    last_failed: bool = False

@dataclass
class UpdateCommandArgs:
    lib_path: Optional[path]
    package: Optional[str]

@dataclass
class UpgradeCommandArgs:
    pass