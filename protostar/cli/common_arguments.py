from protostar.starknet_gateway import SUPPORTED_BLOCK_EXPLORER_NAMES

from .protostar_argument import ProtostarArgument

LIB_PATH_ARG = ProtostarArgument(
    name="lib-path",
    description="Directory containing project dependencies. "
    "This argument is used with the configuration file V2.",
    type="path",
)

block_explorer_list = "\n".join(
    [
        f"- {block_explorer_name}"
        for block_explorer_name in SUPPORTED_BLOCK_EXPLORER_NAMES
    ]
)
BLOCK_EXPLORER_ARG = ProtostarArgument(
    name="block-explorer",
    description=f"Generated links will point to that block explorer. Available values:\n{block_explorer_list}",
    type="block_explorer",
)

ACCOUNT_CLASS_HASH_ARG = ProtostarArgument(
    name="account-class-hash",
    description="Class hash of the declared account contract.",
    type="class_hash",
    is_required=True,
)

ACCOUNT_ADDRESS_SALT_ARG = ProtostarArgument(
    name="account-address-salt",
    description="An arbitrary value used to determine the address of the new contract.",
    type="int",
    is_required=True,
)

ACCOUNT_CONSTRUCTOR_INPUT = ProtostarArgument(
    name="account-constructor-input",
    description="Input to the account's constructor.",
    type="int",
    value_parser="list",
)

COMPILED_CONTRACTS_DIR_ARG = ProtostarArgument(
    name="compiled-contracts-dir",
    description="An output directory used to put the compiled contracts in.",
    type="path",
    default="build",
)

EXTERNAL_DEPENDENCY_REFERENCE_DESCRIPTION = """- `GITHUB_ACCOUNT_NAME/REPO_NAME[@TAG]`
    - `OpenZeppelin/cairo-contracts@v0.4.0`
- `URL_TO_THE_REPOSITORY`
    - `https://github.com/OpenZeppelin/cairo-contracts`
- `SSH_URI`
    - `git@github.com:OpenZeppelin/cairo-contracts.git`
"""

INTERNAL_DEPENDENCY_REFERENCE_DESCRIPTION = (
    EXTERNAL_DEPENDENCY_REFERENCE_DESCRIPTION
    + "- `PACKAGE_DIRECTORY_NAME`\n"
    + "    - `cairo_contracts`, if the package location is `lib/cairo_contracts`"
)

PACKAGE_ARG = ProtostarArgument(
    description=EXTERNAL_DEPENDENCY_REFERENCE_DESCRIPTION,
    name="package",
    type="str",
    is_positional=True,
)


MAX_FEE_ARG = ProtostarArgument(
    name="max-fee",
    description=(
        "The maximum fee that the sender is willing to pay for the transaction. "
        'Provide "auto" to auto estimate the fee.'
    ),
    type="fee",
    is_required=True,
)

WAIT_FOR_ACCEPTANCE_ARG = ProtostarArgument(
    name="wait-for-acceptance",
    description="Waits for transaction to be accepted on chain.",
    type="bool",
    default=False,
)

ABI_PATH_ARG = ProtostarArgument(
    name="abi",
    description=(
        "Path to the ABI file to be used by Data Transformer. "
        "If not provided, Protostar will get the ABI from StarkNet."
    ),
    type="path",
)

ACCOUNT_ADDRESS_ARG = ProtostarArgument(
    name="account-address",
    description="Account address.",
    type="address",
    is_required=True,
)

PRIVATE_KEY_ENV_VAR_NAME = "PROTOSTAR_ACCOUNT_PRIVATE_KEY"

PRIVATE_KEY_PATH_ARG = ProtostarArgument(
    name="private-key-path",
    description="Path to the file, which stores your private key (in hex representation) for the account. \n"
    f"Can be used instead of {PRIVATE_KEY_ENV_VAR_NAME} env variable.",
    type="path",
)

SIGNER_CLASS_ARG = ProtostarArgument(
    name="signer-class",
    description="Custom signer class module path.",
    type="str",
)
