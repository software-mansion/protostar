import re
import sys
from pathlib import Path
from typing import Optional

import tomli
from git.repo import Repo
from packaging import version

# check if the active branch is master
PROJECT_ROOT = Path(__file__).parent.parent
repo = Repo(PROJECT_ROOT)

if str(repo.active_branch) != "master":
    print("Checkout to master and try again.")
    sys.exit(1)

# check if the local master is in sync with the remote master
commits_behind_count = sum(1 for c in repo.iter_commits("master..origin/master"))
commits_ahead_count = sum(1 for c in repo.iter_commits("origin/master..master"))
if commits_ahead_count + commits_behind_count > 0:
    print("`master` is not in sync with the `origin/master`")
    sys.exit(1)

# get current Protostar version
path = PROJECT_ROOT / "pyproject.toml"

new_protostar_version_str: Optional[str] = None
with open(path, "r+", encoding="UTF-8") as file:
    raw_pyproject = file.read()
    pyproject = tomli.loads(raw_pyproject)
    version_str = pyproject["tool"]["poetry"]["version"]
    protostar_version = version.parse(version_str)
    print(f"Current Protostar version: {protostar_version}")

    new_protostar_version_str = input("Provide the incoming Protostar version: ")

    # validate new version
    match_result = re.compile(r"^\d*\.\d*\.\d*$").match(new_protostar_version_str)
    if match_result is None:
        print("Invalid version")
        sys.exit(1)
    new_protostar_version = version.parse(new_protostar_version_str)

    if new_protostar_version <= protostar_version:
        print(f"New version must be greater than {protostar_version}")
        sys.exit(1)


assert new_protostar_version_str is not None

# add tag
tag_name = f"v{new_protostar_version_str}"
tag = repo.create_tag(f"v{new_protostar_version_str}-pre-release", ref="HEAD")

# push to master
origin = repo.remote(name="origin")
origin.push(tag.path)

print((f"Created and pushed tag: {tag_name}"))
print(
    (
        "It may take some time until GitHub action builds and uploads binaries."
        "Double check there the release is marked as pre-release version."
    )
)
