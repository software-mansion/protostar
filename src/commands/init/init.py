from pathlib import Path
import shutil
from colorama import Fore

from src.utils.config.package import Package, PackageConfig


def init(script_root: str):
    """
    Creates init protostar project
    """
    project_name = input(f"{Fore.CYAN}Project name: ")

    project_root = Path() / project_name
    copy_template(script_root, "default", project_root)
    package = Package(project_root=project_root)

    def colored_input(message: str):
        return input(f"{Fore.CYAN}{message}:{Fore.RESET} ")

    project_description = colored_input("Project description")
    author = colored_input("Author")
    version = colored_input("Version")
    project_license = colored_input("License")
    lib_dir = colored_input("Libraries directory name (optional)")

    lib_pth = Path(project_root, lib_dir)

    if lib_dir and not lib_pth.is_dir():
        lib_pth.mkdir(parents=True)

    package.write_config(
        PackageConfig(
            name=project_name,
            description=project_description,
            license=project_license,
            version=version,
            authors=[author],
            libs_path=lib_dir,
        )
    )


def copy_template(script_root: str, template_name: str, project_path: Path):
    template_path = f"{script_root}/templates/{template_name}"
    shutil.copytree(template_path, project_path)
