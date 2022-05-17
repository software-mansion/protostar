from protostar.cli.command import Command

output_shared_argument = Command.Argument(
    name="output",
    short_name="o",
    description="An output directory used to put the compiled contracts in.",
    type="path",
    default="build",
)
