from .protostar_argument import ProtostarArgument

lib_path_arg = ProtostarArgument(
    name="lib-path",
    description="Directory containing project dependencies",
    type="path",
    default="lib",
)
