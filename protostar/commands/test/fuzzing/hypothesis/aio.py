import asyncio
import contextvars
import functools
import inspect
from typing import Callable, Awaitable, Any


async def to_thread(func, *args, **kwargs):
    """
    Asynchronously run function *func* in a separate thread.

    Any *args and **kwargs supplied for this function are directly passed
    to *func*. Also, the current :class:`contextvars.Context` is propagated,
    allowing context variables from the main thread to be accessed in the
    separate thread.

    Return a coroutine that can be awaited to get the eventual result of *func*.

    Borrowed from Python 3.9
    """

    loop = asyncio.get_running_loop()
    ctx = contextvars.copy_context()
    func_call = functools.partial(ctx.run, func, *args, **kwargs)
    return await loop.run_in_executor(None, func_call)


def wrap_in_sync(func: Callable[..., Awaitable[Any]]):
    """
    Return a sync wrapper around an async function executing it in separate event loop.

    Separate event loop is used, because Hypothesis engine is running in current executor
    and is effectively blocking it.

    Partially borrowed from pytest-asyncio.
    """

    @functools.wraps(func)
    def inner(*args, **kwargs):
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
