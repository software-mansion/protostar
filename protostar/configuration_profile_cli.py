from protostar.argument_parser import Argument, CLIApp


class ConfigurationProfileCLI(CLIApp):
    PROFILE_ARG = Argument(
        name="profile",
        short_name="p",
        type="str",
        description="Specifies active configuration profile defined in the configuration file.",
    )

    def __init__(self) -> None:
        super().__init__(
            commands=[],
            root_args=[ConfigurationProfileCLI.PROFILE_ARG],
        )
