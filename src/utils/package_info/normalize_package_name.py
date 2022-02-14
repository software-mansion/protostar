def normalize_package_name(package_name: str) -> str:
    return package_name.replace("-", "_").replace(".", "_")
