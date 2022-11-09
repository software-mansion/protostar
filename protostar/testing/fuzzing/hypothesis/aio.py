import asyncio
import functools
import inspect
from typing import Callable, Awaitable, Any


def wrap_in_sync(func: Callable[..., Awaitable[Any]]):
    """
    Return a sync wrapper around an async function executing it in separate event loop.

    Separate event loop is used, because Hypothesis engine is running in current executor
    and is effectively blocking it.

    Partially borrowed from pytest-asyncio.
    """

    @functools.wraps(func)
    def inner(*args: Any, **kwargs: Any):
        coro = func(*args, **kwargs)
        assert inspect.isawaitable(coro)

        loop = asyncio.new_event_loop()
        task = asyncio.ensure_future(coro, loop=loop)
        try:
            loop.run_until_complete(task)
        except BaseException:
            # run_until_complete doesn't get the result from exceptions
            # that are not subclasses of `Exception`.
            # Consume all exceptions to prevent asyncio's warning from logging.
            if task.done() and not task.cancelled():
                task.exception()
            raise

    return inner
