import subprocess

import pytest


# Needed because of bug in newer git versions https://bugs.launchpad.net/ubuntu/+source/git/+bug/1993586
@pytest.fixture(autouse=True)
def enable_file_transport():
    subprocess.run(
        ["git", "config", "--global", "protocol.file.allow", "always"],
        stderr=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        check=True,
    )
    yield
    subprocess.run(
        ["git", "config", "--global", "--unset", "protocol.file.allow"],
        stderr=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        check=True,
    )
