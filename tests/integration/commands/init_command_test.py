from pathlib import Path
from filecmp import dircmp, cmpfiles

import pytest

from protostar.cairo import CairoVersion
from tests.integration.conftest import CreateProtostarProjectFixture
from tests.conftest import PROJECT_ROOT


@pytest.mark.parametrize("cairo_version", [CairoVersion.cairo0, CairoVersion.cairo0])
def test_init(
    create_protostar_project: CreateProtostarProjectFixture, cairo_version: CairoVersion
):
    with create_protostar_project(cairo_version):
        mocker_project_path = Path(".")
        template_project_path = PROJECT_ROOT.joinpath("templates", cairo_version.value)

        dir_compare_object = dircmp(mocker_project_path, template_project_path)
        assert compare_directories(dir_compare_object)


def compare_directories(dcmp: dircmp):
    if dcmp.left_only or dcmp.right_only or dcmp.diff_files:
        return False

    _, diff, errors = cmpfiles(dcmp.left, dcmp.right, dcmp.same_files, shallow=False)
    if diff or errors:
        return False

    for sub_dcmp in dcmp.subdirs.values():
        if not compare_directories(sub_dcmp):
            return False

    return True
