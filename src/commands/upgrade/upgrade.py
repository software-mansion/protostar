from logging import getLogger
from pathlib import Path
import shutil
import os
import requests
from urllib.request import urlretrieve
import tarfile

logget = getLogger()

PROTOSTAR_REPO = "https://github.com/software-mansion/protostar"
PROTOSTAR_DIR = "~/.protostar"


def get_latest_release():
    headers = {'Accept': 'application/json'}
    response = requests.get(
        f'{PROTOSTAR_REPO}/releases/latest',
        headers=headers
    )
    return response.json()


def get_platform():
    platform = os.uname()[0]
    if platform == "Darwin":
        return "macOS"
    if platform == "Linux":
        return "Linux"


def upgrade() -> None:
    platform = get_platform()
    lastest_release = get_latest_release()
    # TODO check if up to date then skip

    old_version = PROTOSTAR_DIR / "previous_version_tmp"
    shutil.move(PROTOSTAR_DIR / "dist", old_version)

    tarball_name = f"protostar-{platform}.tar.gz"
    tarball_loc = PROTOSTAR_DIR / tarball_name

    download_url = f"{PROTOSTAR_REPO}/releases/download/{lastest_release['tag_name']}/{tarball_name}"
    urlretrieve(download_url, tarball_loc)

    tar = tarfile.open(tarball_loc, "r:gz")
    tar.extractall(PROTOSTAR_DIR)
    tar.close()

    # rollback
    os.remove(tarball_loc)
    shutil.rmtree(old_version)
    return
