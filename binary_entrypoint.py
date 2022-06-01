import sys, os, certifi
from pathlib import Path

if __name__ == "__main__":
    try:
        from protostar import main

        # Use certifi certs to avoid problems on mac os
        os.environ["SSL_CERT_FILE"] = certifi.where()
        print(os.environ["SSL_CERT_FILE"])

        main(Path(__file__).parent)

    except ImportError as err:
        # pylint: disable=no-member
        if err.msg.startswith("Failed to initialize: Bad git executable."):
            print(
                "Protostar requires git executable to be specified in $PATH. Did you install git?"
            )
            sys.exit()
        raise err
