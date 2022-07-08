import pytest
from pytest_mock import MockerFixture

from protostar.utils.hook import Hook


@pytest.mark.asyncio
async def test_run_after(mocker: MockerFixture):
    handler = mocker.Mock()

    hook = Hook()
    hook.on(handler)

    async with hook.run_after():
        handler.assert_not_called()
    handler.assert_called_once()

    handler.reset_mock()
    async with hook.run_after():
        handler.assert_not_called()
    handler.assert_not_called()
