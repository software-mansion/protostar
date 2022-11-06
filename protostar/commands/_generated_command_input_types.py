from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Optional
from ._types_source_generated_command_input_types import *


@dataclass
class BuildCommandInput(SimpleNamespace):
    cairo_path: Optional[list[directory]]
    disable_hint_validation: bool = False
    compiled_contracts_dir: path = PosixPath("build")


@dataclass
class CairoMigrateCommandInput(SimpleNamespace):
    targets: list[str] = field(default_factory=lambda: ["."])


@dataclass
class CallCommandInput(SimpleNamespace):
    contract_address: address
    function: str
    gateway_url: Optional[str]
    chain_id: Optional[int]
    network: Optional[str]
    inputs: Optional[list[felt]]


@dataclass
class DeclareCommandInput(SimpleNamespace):
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
class DeployCommandInput(SimpleNamespace):
    contract: path
    inputs: Optional[list[felt]]
    token: Optional[str]
    salt: Optional[felt]
    gateway_url: Optional[str]
    chain_id: Optional[int]
    network: Optional[str]
    wait_for_acceptance: bool = False


@dataclass
class DeployAccountCommandInput(SimpleNamespace):
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
class FormatCommandInput(SimpleNamespace):
    target: list[str] = field(default_factory=lambda: ["."])
    check: bool = False
    verbose: bool = False
    ignore_broken: bool = False


@dataclass
class InitCommandInput(SimpleNamespace):
    name: Optional[str]
    existing: bool = False


@dataclass
class InstallCommandInput(SimpleNamespace):
    lib_path: Optional[path]
    package: Optional[str]
    name: Optional[str]


@dataclass
class InvokeCommandInput(SimpleNamespace):
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
class MigrateCommandInput(SimpleNamespace):
    path: path
    gateway_url: Optional[str]
    chain_id: Optional[int]
    network: Optional[str]
    account_address: Optional[address]
    private_key_path: Optional[path]
    signer_class: Optional[str]
    no_confirm: bool = False
    compiled_contracts_dir: path = PosixPath("build")


@dataclass
class MigrateConfigurationFileCommandInput(SimpleNamespace):
    pass


@dataclass
class RemoveCommandInput(SimpleNamespace):
    package: str
    lib_path: Optional[path]


@dataclass
class TestCommandInput(SimpleNamespace):
    ignore: Optional[list[str]]
    cairo_path: Optional[list[directory]]
    seed: Optional[int]
    target: list[str] = field(default_factory=lambda: ["."])
    disable_hint_validation: bool = False
    profiling: bool = False
    no_progress_bar: bool = False
    safe_collecting: bool = False
    exit_first: bool = False
    report_slowest_tests: int = 0
    last_failed: bool = False


@dataclass
class UpdateCommandInput(SimpleNamespace):
    lib_path: Optional[path]
    package: Optional[str]


@dataclass
class UpgradeCommandInput(SimpleNamespace):
    pass
