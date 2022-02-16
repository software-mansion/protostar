from os import listdir

from src.protostar_exception import ProtostarException
from src.utils.load_normalized_to_real_name_map import load_normalized_to_real_name_map
from src.utils.package_info import extract_info_from_repo_id, normalize_package_name


class PackageNameRetrievalException(ProtostarException):
    pass


def retrieve_real_package_name(
    package_id: str, root_repo_dir: str, packages_dir: str
) -> str:
    normalized_package_name = ""
    if "/" in package_id:
        normalized_package_name = extract_info_from_repo_id(package_id).name
    else:
        normalized_package_name = normalize_package_name(package_id)

    mapping = load_normalized_to_real_name_map(root_repo_dir, packages_dir)

    if normalized_package_name in mapping:
        return mapping[normalized_package_name]

    # custom name
    package_names = listdir(packages_dir)
    if normalized_package_name in package_names:
        return normalized_package_name

    raise PackageNameRetrievalException(
        f'Protostar couldn\'t find package "{package_id}".'
    )
