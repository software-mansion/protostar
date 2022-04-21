# TODO: REMOVE FILE BEFORE PUSH/MERGE!

from argparse import ArgumentParser
from typing import List, Optional

from src.application import AbstractCommand, Application, ArgumentParserFacade


class FooCommand(AbstractCommand):
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
    def arguments(self) -> List[AbstractCommand.Argument]:
        return [
            AbstractCommand.Argument(
                name="foo",
                description="foo_desc",
                example="FOO --foo",
                input_type="bool",
                is_required=False,
                is_array=False,
            ),
            AbstractCommand.Argument(
                name="bar",
                description="foo_desc",
                example="FOO --foo",
                input_type="bool",
                is_required=False,
                is_array=False,
            ),
        ]

    async def run(self):
        pass


app = Application(commands=[FooCommand()], root_args=[])
parser = ArgumentParserFacade(ArgumentParser())
parser = app.setup_parser(parser)

print(parser.parse())
