from .multicall_use_case import MulticallUseCase, MulticallInput, MulticallOutput


async def test_multicall_use_case_happy_case():
    multicall = MulticallUseCase()

    result = await multicall.execute(MulticallInput())

    assert MulticallOutput() == result
