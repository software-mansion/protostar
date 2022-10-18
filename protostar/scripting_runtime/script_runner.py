import runpy
import sys
import traceback
from multiprocessing import Process
from pathlib import Path


class ScriptRunner:
    @staticmethod
    def run(path: Path) -> None:
        """
        Runs a Python script (given by ``path``) in a subprocess forked from Protostar's process.
        The script is **not** interpreted in sandbox mode.
        """

        path_str = str(path)

        process = Process(target=_bootstrap, args=(path_str,), name=path_str)
        process.start()
        process.join()
        process.close()


def _bootstrap(script_path: str) -> None:
    try:
        runpy.run_path(script_path, run_name="__main__")
    except Exception:  # pylint: disable=broad-except
        limit = _count_script_traceback_frames(script_path)

        print(f"Script {script_path}:", file=sys.stderr)
        traceback.print_exc(limit=-limit, file=sys.stderr)


def _count_script_traceback_frames(script_path: str) -> int:
    """
    Finds how many last frames in current exception's traceback belong to the executed script.

    In other words, passing returned number, in negative, as a ``limit`` to any of the
    ``traceback`` module's functions will trim the traceback only to show script's frames,
    excluding any Protostar's internal noise.
    """

    tb = sys.exc_info()[2]
    summary = traceback.extract_tb(tb)

    count = 0
    for frame in summary:
        if frame.filename == script_path:
            break

        count += 1

    return len(summary) - count
