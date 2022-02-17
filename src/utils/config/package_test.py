from src.utils.config.package import Package, PackageConfig


def mock_package(mocker, contracts, libs_path) -> Package:
    pkg = Package()
    mock_config = PackageConfig(
        name="",
        description="",
        license="",
        version="",
        authors=[""],
        contracts=contracts,
        libs_path=libs_path,
    )
    mocker.patch.object(pkg, attribute="load_config").return_value = mock_config
    return pkg
