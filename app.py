# TODO: REMOVE FILE BEFORE PUSH/MERGE!

import sys
from argparse import ArgumentParser
from typing import List, Optional

from src.core import Application, ArgumentParserFacade, Command


class FooCommand(Command):
    @property
    def name(self) -> str:
        return "FOO"

    @property
    def description(self) -> str:
        return "FOO_DESC"

    @property
    def example(self) -> Optional[str]:
        return "$ foo"

    @property
    def arguments(self) -> List[Command.Argument]:
        return [
            Command.Argument(
                name="foo",
                description="foo_desc",
                input_type="directory",
                is_required=False,
                is_array=False,
            ),
        ]

    async def run(self, args):
        pass


app = Application(commands=[FooCommand()], root_args=[])
parser = ArgumentParserFacade(ArgumentParser(), app)

print(sys.argv[1:])
print(parser.parse())
