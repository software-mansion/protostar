import sys
from pathlib import Path

if __name__ == "__main__":
    try:
        from src import main

        main(Path(__file__).parent)

    except ImportError as err:
        # pylint: disable=no-member
        if err.msg.startswith("Failed to initialize: Bad git executable."):
            print(
                "Protostar requires git executable to be specified in $PATH. Did you install git?"
            )
            sys.exit()
        raise err
