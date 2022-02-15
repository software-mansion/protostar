from typing import Optional

from src.utils.load_normalized_to_real_name_map import load_normalized_to_real_name_map
from src.utils.package_info.extract_info_from_repo_id import extract_info_from_repo_id
from src.utils.package_info.normalize_package_name import normalize_package_name


def retrieve_real_package_name(
    package_id: str, root_repo_dir: str, packages_dir: str
) -> Optional[str]:
    normalized_package_name = ""
    if "/" in package_id:
        normalized_package_name = extract_info_from_repo_id(package_id).name
    else:
        normalized_package_name = normalize_package_name(package_id)

    mapping = load_normalized_to_real_name_map(root_repo_dir, packages_dir)

    if normalized_package_name in mapping:
        return mapping[normalized_package_name]

    return None
