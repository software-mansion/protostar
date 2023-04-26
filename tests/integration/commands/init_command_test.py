from pathlib import Path
from filecmp import dircmp, cmpfiles

from protostar.cairo import CairoVersion
from tests.integration.conftest import CreateProtostarProjectFixture
from tests.conftest import PROJECT_ROOT


def test_init_cairo0(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project(CairoVersion.cairo0):
        mocker_project_path = Path(".")
        template_project_path = PROJECT_ROOT.joinpath(
            "templates", CairoVersion.cairo0.value
        )

        dir_compare_object = dircmp(mocker_project_path, template_project_path)
        compare_directories(dir_compare_object)


def test_init_cairo1(
    create_protostar_project: CreateProtostarProjectFixture, datadir: Path
):
    with create_protostar_project(CairoVersion.cairo1):
        mocker_project_path = Path(".")
        template_project_path = datadir / "project_name"

        dir_compare_object = dircmp(mocker_project_path, template_project_path)
        compare_directories(dir_compare_object)


def compare_directories(dcmp: dircmp):
    assert not (dcmp.left_only or dcmp.right_only or dcmp.diff_files), (
        f"files with different os.stat() (probably different content) signatures: {dcmp.diff_files}\n "
        f"files not present in real templates directory: {dcmp.left_only}\n"
        f"files not present in mock templates directory: {dcmp.right_only}"
    )

    _, diff, errors = cmpfiles(dcmp.left, dcmp.right, dcmp.same_files, shallow=False)

    assert not (diff or errors), (
        f"files with different content: {diff}\n"
        f"files which could not be compared: {errors}"
    )

    for sub_dcmp in dcmp.subdirs.values():
        compare_directories(sub_dcmp)
