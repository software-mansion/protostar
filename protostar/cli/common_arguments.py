from .protostar_argument import ProtostarArgument

LIB_PATH_ARG = ProtostarArgument(
    name="lib-path",
    description="Directory containing project dependencies. "
    "This argument is used with the configuration file V2.",
    type="path",
)
