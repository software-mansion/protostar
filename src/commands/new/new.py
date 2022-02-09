import shutil
from pathlib import Path

from src.commands.common import PackageConfig


def new(project_name: str, script_root: str):
    """
    Creates new protostar project
    """
    project_path = Path() / project_name
    copy_template(script_root, "default", project_path)

    package = PackageConfig(project_path=project_path)
    package.name = project_name
    package.write()


def copy_template(script_root: str, template_name: str, project_path: Path):
    template_path = f"{script_root}/templates/{template_name}"
    shutil.copytree(template_path, project_path)
