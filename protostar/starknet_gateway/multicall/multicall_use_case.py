from dataclasses import dataclass

from protostar.architecture import UseCase


@dataclass(frozen=True)
class MulticallInput:
    pass


@dataclass(frozen=True)
class MulticallOutput:
    pass


class MulticallUseCase(UseCase[MulticallInput, MulticallOutput]):
    async def execute(self, data: MulticallInput):
        return MulticallOutput()
