from dataclasses import replace

from typing_extensions import Self

from protostar.argument_parser import Argument

from .protostar_arg_type import ProtostarArgTypeName


class ProtostarArgument(Argument[ProtostarArgTypeName]):
    def copy_with_description(self, description: str) -> Self:
        return replace(self, description=description)
