import argparse
from abc import ABC, abstractmethod
from argparse import ArgumentParser
from typing import Any, List, Optional, Union

from attr import dataclass
from typing_extensions import Literal

InputAllowedType = Literal["string", "Path[]", "number", "bool"]


@dataclass
class Argument:
    name: str
    description: str
    input_type: InputAllowedType
    is_positional: bool
    example: Optional[str]


class AbstractCommand(ABC):
    @property
    def name(self) -> str:
        ...

    @property
    def description(self) -> str:
        ...

    @property
    def example(self) -> Optional[str]:
        ...

    def __init__(self, arguments: List[Argument]) -> None:
        super().__init__()

        self.arguments = arguments

    @abstractmethod
    def run(self):
        ...


class ArgumentCommandParserFacade:
    def __init__(self, argument_parser: ArgumentParser) -> None:
        self.argument_parser = argument_parser

    def add_argument(self, argument: Argument) -> "ArgumentCommandParserFacade":
        self.argument_parser.add_argument()
        return self


class ArgumentParserFacade(ArgumentCommandParserFacade):
    def __init__(self, argument_parser: ArgumentParser) -> None:
        super().__init__(argument_parser)
        self.argument_parser = argument_parser
        self.command_parsers = self.argument_parser.add_subparsers(dest="command")

    def add_command(self, name: str) -> ArgumentCommandParserFacade:
        return ArgumentCommandParserFacade(
            self.command_parsers.add_parser(
                name,
                formatter_class=argparse.RawTextHelpFormatter,
            )
        )

    def parse(self) -> Any:
        return self.argument_parser.parse_args()


class Application:
    def __init__(
        self,
        argument_parser: ArgumentParserFacade,
        inputs: List[Union[Argument, AbstractCommand]],
    ) -> None:
        self.argument_parser = argument_parser
        self.inputs = inputs

    async def run(self, args: Any):
        pass
