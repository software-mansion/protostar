import re
import sys
from pathlib import Path
from typing import Optional

import tomli
from git.repo import Repo
from packaging import version

# check if the active branch is master
SCRIPT_ROOT = Path(__file__).parent
repo = Repo(SCRIPT_ROOT)

if not repo.active_branch == "master":
    print("Checkout to master and try again.")
    sys.exit(1)

# get current Protostar version
path = SCRIPT_ROOT / "pyproject.toml"

new_protostar_version_str: Optional[str] = None
with open(path, "r+", encoding="UTF-8") as file:
    raw_pyproject = file.read()
    pyproject = tomli.loads(raw_pyproject)
    version_str = pyproject["tool"]["poetry"]["version"]
    protostar_version = version.parse(version_str)
    print(f"Current Protostar version: {protostar_version}")

    # prompt new Protostar version
    new_protostar_version_str = input("Provide the new Protostar version: ")

    # validate new version
    match_result = re.compile(r"^\d*\.\d*\.\d*$").match(new_protostar_version_str)
    if match_result is None:
        print("Invalid syntax")
        sys.exit(1)
    new_protostar_version = version.parse(new_protostar_version_str)

    if new_protostar_version <= protostar_version:
        print(f"New version must be greater than {protostar_version}")
        sys.exit(1)

    # update version in protostar.toml
    file.seek(0)
    file.truncate()
    file.write(
        raw_pyproject.replace(
            f'version = "{protostar_version}"', f'version = "{new_protostar_version}"'
        )
    )


# add commit
assert new_protostar_version_str is not None
repo.git.add("pyproject.toml")
commit = repo.index.commit(
    f"update version in pyproject.toml ({new_protostar_version_str})"
)

# add tag
repo.create_tag(f"v{new_protostar_version_str}")

# push to master
origin = repo.remote(name="origin")
origin.push()
