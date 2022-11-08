from protostar.starknet_gateway import SUPPORTED_BLOCK_EXPLORER_NAMES

from .protostar_argument import ProtostarArgument

LIB_PATH_ARG = ProtostarArgument(
    name="lib-path",
    description="Directory containing project dependencies. "
    "This argument is used with the configuration file V2.",
    type="path",
)

BLOCK_EXPLORER_ARG = ProtostarArgument(
    name="block_explorer",
    description=f"""Generated links will point to that block explorer. Available values: {[f"- {block_explorer_name}" for block_explorer_name in SUPPORTED_BLOCK_EXPLORER_NAMES]}""",
    type="block_explorer",
    default="starkscan",
)
