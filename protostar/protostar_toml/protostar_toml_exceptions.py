from protostar.protostar_exception import ProtostarException


class NoProtostarProjectFoundException(ProtostarException):
    pass


class VersionNotSupportedException(ProtostarException):
    pass


class InvalidProtostarTOMLException(ProtostarException):
    def __init__(self, section_name: str):
        self.section_name = section_name
        super().__init__(section_name)

    def __str__(self) -> str:
        return "\n".join(
            [
                "Invalid 'protostar.toml' configuration.",
                f"Couldn't load [protostar.{self.section_name}]",
            ]
        )
