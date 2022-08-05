from protostar.cli import CLIApp, Command


class ConfigurationProfileCLI(CLIApp):
    PROFILE_ARG = Command.Argument(
        name="profile",
        short_name="p",
        type="str",
        description="\n".join(
            [
                "Specifies active profile configuration. This argument can't be configured in `protostar.toml`.",
                "#### CI configuration",
                '```toml title="protostar.toml"',
                "[profile.ci.protostar.shared_command_configs]",
                "no_color=true",
                "```",
                "`protostar -p ci test`",
                "",
                "#### Deployment configuration",
                '```toml title="protostar.toml"',
                "[profile.devnet.protostar.deploy]",
                'gateway_url="http://127.0.0.1:5050/"',
                "```",
                "`protostar -p devnet deploy ...`" "",
            ]
        ),
    )

    def __init__(self) -> None:
        super().__init__(
            commands=[],
            root_args=[ConfigurationProfileCLI.PROFILE_ARG],
        )
