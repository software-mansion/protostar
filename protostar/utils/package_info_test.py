# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument

from os import mkdir
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from protostar.utils.create_and_commit_sample_file import create_and_commit_sample_file
from protostar.utils.package_info import (
    IncorrectURL,
    InvalidPackageName,
    PackageInfo,
    PackageNameRetrievalException,
    _map_ssh_to_url,
    extract_info_from_repo_id,
    load_normalized_to_real_name_map,
    retrieve_real_package_name,
)

from protostar.git import Git


class ExtractInfoFromRepoIdTest:
    def test_github(self):
        package_info = extract_info_from_repo_id(
            "https://github.com/software-mansion/protostar"
        )

        assert package_info.name == "protostar"
        assert package_info.version is None
        assert package_info.url == "https://github.com/software-mansion/protostar"

    def test_dashes(self):
        package_info = extract_info_from_repo_id(
            "https://github.com/software-mansion/protostar-test"
        )

        assert package_info.name == "protostar_test"
        assert package_info.version is None
        assert package_info.url == "https://github.com/software-mansion/protostar-test"

    def test_bitbucket(self):
        package_info = extract_info_from_repo_id(
            "https://bitbucket.org/atlassian/python-bitbucket"
        )

        assert package_info.name == "python_bitbucket"
        assert package_info.version is None
        assert package_info.url == "https://bitbucket.org/atlassian/python-bitbucket"

    def test_ssh_and_dot(self):
        package_info = extract_info_from_repo_id(
            "git@github.com:software-mansion/starknet.py.git"
        )

        assert package_info.name == "starknet_py"
        assert package_info.version is None
        assert package_info.url == "https://github.com/software-mansion/starknet.py"

    def test_account_repo_name(self):
        package_info = extract_info_from_repo_id("software-mansion/protostar")

        assert package_info.name == "protostar"
        assert package_info.version is None
        assert package_info.url == "https://github.com/software-mansion/protostar"

    def test_tags(self):
        package_info = extract_info_from_repo_id(
            "software-mansion/protostar@0.0.0-alpha"
        )

        assert package_info.name == "protostar"
        assert package_info.version == "0.0.0-alpha"
        assert package_info.url == "https://github.com/software-mansion/protostar"

    def test_slash_at_the_end(self):
        package_info = extract_info_from_repo_id(
            "https://github.com/software-mansion/protostar/"
        )

        assert package_info.name == "protostar"
        assert package_info.version is None
        assert package_info.url == "https://github.com/software-mansion/protostar/"

    def test_incorrect_url(self):
        with pytest.raises(IncorrectURL):
            extract_info_from_repo_id("https://github.com/software-mansion")

    def test_failure_at_extracting_slug_from_ssh(self):
        with pytest.raises(IncorrectURL):
            extract_info_from_repo_id("git@github.com:software-mansion/starknet.py")

    def test_failure_at_unknown_repo_id_format(self):
        with pytest.raises(InvalidPackageName):
            extract_info_from_repo_id("http://github.pl/foobar.git")

    def test_failure_at_mapping_ssh_to_url(self):
        with pytest.raises(InvalidPackageName):
            _map_ssh_to_url("abc@github.com:software-mansion/starknet.py.git")


class LoadNormalizedToRealNameMapTest:

    # - repo_with_normal_name_package
    #   - lib
    #     - package (s)
    # - repo_with_custom_name_package
    #   - lib
    #     - pkg (s)
    # - package_repo
    #   - foo.txt

    @pytest.fixture
    def package_normal_name(self):
        return "package"

    @pytest.fixture
    def package_custom_name(self):
        return "pkg"

    @pytest.fixture
    def packages_dir_name(self):
        return "lib"

    @pytest.fixture
    def repo_with_normal_name_package_dir(self, tmpdir) -> Path:
        return Path(tmpdir) / "repo_a"

    @pytest.fixture
    def repo_with_custom_name_package_dir(self, tmpdir) -> Path:
        return Path(tmpdir) / "repo_b"

    @pytest.fixture
    def package_repo_dir(self, tmpdir) -> Path:
        return Path(tmpdir) / "package_repo"

    @pytest.fixture
    def package_repo(self, package_repo_dir: Path):
        repo = Git.init(package_repo_dir)

        create_and_commit_sample_file(repo, package_repo_dir)

        return repo

    @pytest.fixture
    def repo_with_normal_name_package(
        self,
        package_repo,
        repo_with_normal_name_package_dir: Path,
        package_normal_name: str,
        packages_dir_name: str,
        package_repo_dir: Path,
    ):
        repo = Git.init(repo_with_normal_name_package_dir)

        packages_dir = repo_with_normal_name_package_dir / packages_dir_name
        mkdir(packages_dir)

        repo.add_submodule(
            url=str(package_repo_dir),
            submodule_path=packages_dir / package_normal_name,
            name=package_normal_name,
        )

        repo.add(repo.repo_path)
        repo.commit("add package")

    @pytest.fixture
    def repo_with_custom_name_package(
        self,
        package_repo,
        repo_with_custom_name_package_dir: Path,
        package_custom_name: str,
        packages_dir_name: str,
        package_repo_dir: Path,
    ):
        repo = Git.init(repo_with_custom_name_package_dir)

        packages_dir = repo_with_custom_name_package_dir / packages_dir_name
        mkdir(packages_dir)

        repo.add_submodule(
            url=str(package_repo_dir),
            submodule_path=packages_dir / package_custom_name,
            name=package_custom_name,
        )

        repo.add(repo.repo_path)
        repo.commit("add package")

    @pytest.mark.usefixtures("repo_with_normal_name_package")
    def test_package_installed_without_custom_name(
        self,
        repo_with_normal_name_package_dir: Path,
        package_normal_name: str,
        packages_dir_name: str,
        mocker: MockerFixture,
    ):

        mocked_extract_info_from_repo_id = mocker.patch(
            "protostar.utils.package_info.extract_info_from_repo_id",
        )
        mocked_extract_info_from_repo_id.return_value = PackageInfo(
            name=package_normal_name, url="", version=None
        )

        mapping = load_normalized_to_real_name_map(
            repo_dir=repo_with_normal_name_package_dir,
            packages_dir=repo_with_normal_name_package_dir / packages_dir_name,
        )

        assert mapping[package_normal_name] == package_normal_name

    @pytest.mark.usefixtures("repo_with_custom_name_package")
    def test_package_installed_with_custom_name(
        self,
        repo_with_custom_name_package_dir: Path,
        package_custom_name: str,
        package_normal_name: str,
        packages_dir_name: str,
        mocker: MockerFixture,
    ):

        mocked_extract_info_from_repo_id = mocker.patch(
            "protostar.utils.package_info.extract_info_from_repo_id",
        )
        mocked_extract_info_from_repo_id.return_value = PackageInfo(
            name=package_normal_name, url="", version=None
        )

        mapping = load_normalized_to_real_name_map(
            repo_dir=repo_with_custom_name_package_dir,
            packages_dir=repo_with_custom_name_package_dir / packages_dir_name,
        )

        assert mapping[package_normal_name] == package_custom_name


class RetrieveRealPackageNameTest:
    @pytest.fixture
    def repo_root_dir(self, tmpdir) -> Path:
        repo_dir = Path(tmpdir) / "repo"
        mkdir(repo_dir)
        return repo_dir

    @pytest.fixture
    def packages_dir(self, repo_root_dir: Path) -> Path:
        packages_dir = repo_root_dir / "lib"
        mkdir(packages_dir)
        return packages_dir

    @pytest.fixture
    def package_name(self):
        return "package"

    @pytest.fixture
    def package_dir(self, packages_dir: Path, package_name: str) -> Path:
        package_dir = packages_dir / package_name
        mkdir(package_dir)
        return package_dir

    @pytest.mark.parametrize("package_name", ["starknet_py"])
    @pytest.mark.usefixtures("package_dir")
    def test_name_supported_by_install_command(
        self,
        repo_root_dir: Path,
        packages_dir: Path,
        package_name: str,
        mocker: MockerFixture,
    ):
        mocked_load_normalized_to_real_name_map = mocker.patch(
            "protostar.utils.package_info.load_normalized_to_real_name_map",
        )
        mocked_load_normalized_to_real_name_map.return_value = {
            "starknet_py": "starknet_py",
        }

        result = retrieve_real_package_name(
            "software-mansion/starknet.py", repo_root_dir, packages_dir
        )

        mocked_load_normalized_to_real_name_map.assert_called_once()
        assert result == package_name

    @pytest.mark.parametrize("package_name", ["starknet_py"])
    @pytest.mark.usefixtures("package_dir")
    def test_not_normalized_name(
        self,
        repo_root_dir: Path,
        packages_dir: Path,
        package_name: str,
        mocker: MockerFixture,
    ):
        mocked_load_normalized_to_real_name_map = mocker.patch(
            "protostar.utils.package_info.load_normalized_to_real_name_map",
        )
        mocked_load_normalized_to_real_name_map.return_value = {
            "starknet_py": "starknet_py",
        }

        result = retrieve_real_package_name("starknet.py", repo_root_dir, packages_dir)

        mocked_load_normalized_to_real_name_map.assert_called_once()
        assert result == package_name

    @pytest.mark.parametrize("package_name", ["sn"])
    @pytest.mark.usefixtures("package_dir")
    def test_package_custom_name(
        self,
        repo_root_dir: Path,
        packages_dir: Path,
        package_name: str,
        mocker: MockerFixture,
    ):
        mocked_load_normalized_to_real_name_map = mocker.patch(
            "protostar.utils.package_info.load_normalized_to_real_name_map",
        )
        mocked_load_normalized_to_real_name_map.return_value = {
            "starknet_py": "sn",
        }

        result = retrieve_real_package_name("starknet.py", repo_root_dir, packages_dir)

        mocked_load_normalized_to_real_name_map.assert_called_once()
        assert result == package_name

    @pytest.mark.parametrize("package_name", ["sn"])
    @pytest.mark.usefixtures("package_dir")
    def test_not_existing_package(
        self,
        repo_root_dir: Path,
        packages_dir: Path,
        mocker: MockerFixture,
    ):
        mocked_load_normalized_to_real_name_map = mocker.patch(
            "protostar.utils.package_info.load_normalized_to_real_name_map",
        )
        mocked_load_normalized_to_real_name_map.return_value = {
            "starknet_py": "sn",
        }

        with pytest.raises(PackageNameRetrievalException):
            retrieve_real_package_name(
                "NOT_EXISTING_PACKAGE", repo_root_dir, packages_dir
            )
