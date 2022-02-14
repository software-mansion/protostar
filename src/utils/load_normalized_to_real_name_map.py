from os import listdir
from typing import Dict

from git.repo import Repo

from src.utils.package_info.extract_info_from_repo_id import extract_info_from_repo_id


def load_normalized_to_real_name_map(repo_root_dir: str, packages_dir: str):
    repo = Repo.init(repo_root_dir)

    mapping: Dict["str", "str"] = {}

    package_names = listdir(packages_dir)
    for submodule in repo.submodules:
        if submodule.name in package_names:
            normalized_package_name = extract_info_from_repo_id(submodule.url).name
            mapping[normalized_package_name] = submodule.name

    return mapping
