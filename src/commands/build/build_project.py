import json
from pathlib import Path
from typing import List

from src.commands.test.utils import collect_immediate_subdirectories
from src.utils.config.project import Project
from src.utils.starknet_compilation import StarknetCompiler


def build_project(
    project: Project,
    output_dir: Path,
    cairo_path: List[Path],
    disable_hint_validation: bool,
):
    pkg_config = project.load_config()
    libraries_root = Path(pkg_config.libs_path)

    project_paths = [
        str(project.project_root),
        str(libraries_root),
        *collect_immediate_subdirectories(libraries_root),
        *[str(pth) for pth in cairo_path],
    ]
    output_dir.mkdir(exist_ok=True)

    for contract_name, contract_components in pkg_config.contracts.items():
        contract = StarknetCompiler(
            include_paths=project_paths, disable_hint_validation=disable_hint_validation,
        ).compile_contract(
            *[Path(component) for component in contract_components],
        )

        with open(
            Path(output_dir, f"{contract_name}.json"), mode="w", encoding="utf-8"
        ) as output_file:
            json.dump(
                contract.Schema().dump(contract), output_file, indent=4, sort_keys=True
            )
            output_file.write("\n")

        with open(
            Path(output_dir, f"{contract_name}_abi.json"), mode="w", encoding="utf-8"
        ) as output_abi_file:
            json.dump(contract.abi, output_abi_file, indent=4, sort_keys=True)
            output_abi_file.write("\n")
