import re
import sys
from pathlib import Path
from typing import Optional

import tomli
import tomli_w
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

    is_breaking_v = input(
        "Does this version contain breaking changes to protostar.toml structure? (y/n): "
    )
    is_breaking_v = is_breaking_v.lower()
    if is_breaking_v not in ["y", "n"]:
        print(f'"{is_breaking_v}" is not a valid option')
        sys.exit(1)

    # update version in pyproject.toml
    pyproject["tool"]["poetry"]["version"] = new_protostar_version_str

    breaking_versions = pyproject["tool"]["protostar"]["breaking_versions"]
    if is_breaking_v:
        breaking_versions.append(new_protostar_version_str)

    file.seek(0)
    file.truncate()
    file.write(tomli_w.dumps(pyproject))


# add commit
assert new_protostar_version_str is not None
repo.git.add("pyproject.toml")
commit = repo.index.commit(f"release Protostar {new_protostar_version_str}")

# add tag
tag_name = f"v{new_protostar_version_str}"
tag = repo.create_tag(tag_name, ref=commit.hexsha)

# push to master
origin = repo.remote(name="origin")
origin.push()
origin.push(tag.path)

print(f"Created and pushed tag: {tag_name}")
print("It may take some time until GitHub action builds and uploads binaries.")
