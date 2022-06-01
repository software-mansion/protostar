from pathlib import Path
from typing import Optional

import tomli
from git.repo import Repo
from packaging import version

# check if the active branch is master
PROJECT_ROOT = Path(__file__).parent.parent
repo = Repo(PROJECT_ROOT)

# get current Protostar version
path = PROJECT_ROOT / "pyproject.toml"

new_protostar_version_str: Optional[str] = None
with open(path, "r+", encoding="UTF-8") as file:
    raw_pyproject = file.read()
    pyproject = tomli.loads(raw_pyproject)
    version_str = pyproject["tool"]["poetry"]["version"]
    protostar_version = version.parse(version_str)
    print(f"Current Protostar version: {protostar_version}")
    
    new_protostar_version_str = input("Provide the new Protostar version: ")
    new_protostar_version_str += "-pre-release"

assert new_protostar_version_str is not None

tag = repo.create_tag(f"v{new_protostar_version_str}", ref='HEAD')

# push to master
origin = repo.remote(name="origin")
origin.push()
origin.push(tag.path)
