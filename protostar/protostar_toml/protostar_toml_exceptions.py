from typing import Optional

from protostar.protostar_exception import ProtostarException


class NoProtostarProjectFoundException(ProtostarException):
    pass


class VersionNotSupportedException(ProtostarException):
    pass


class InvalidProtostarTOMLException(ProtostarException):
    def __init__(self, section_name: str, attribute_name: Optional[str] = None):
        self.section_name = section_name
        self.attribute_name = attribute_name
        msg = (
            f"Couldn't load [protostar.{self.section_name}]::{self.attribute_name}"
            if self.attribute_name
            else f"Couldn't load [protostar.{self.section_name}]"
        )
        super().__init__(
            "\n".join(
                [
                    "Invalid 'protostar.toml' configuration.",
                    msg,
                ]
            )
        )
