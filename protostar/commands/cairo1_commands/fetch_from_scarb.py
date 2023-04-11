# pyright: reportUnknownLambdaType=false
from typing import Optional, Dict, List
from pathlib import Path
import os
import json
import subprocess

import logging

from protostar.protostar_exception import ProtostarException


class ScarbMetadataFetchException(ProtostarException):
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(
            "Error while trying to fetch Scarb metadata:\n" + message, details
        )


def has_scarb_toml(project_root_path: Path) -> bool:
    return "Scarb.toml" in os.listdir(project_root_path)


def read_scarb_metadata(scarb_toml_path: Path) -> Dict:
    try:
        result = subprocess.run(
            [
                "scarb",
                "--json",
                "--manifest-path",
                scarb_toml_path,
                "metadata",
                "--format-version",
                "1",
            ],
            check=False,
            cwd=scarb_toml_path.parent,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as ex:
        raise ScarbMetadataFetchException(str(ex)) from ex

    if result.returncode != 0:
        raise ScarbMetadataFetchException(
            "Metadata fetch returned a non-zero exit code."
        )

    # only the last line of the output contains metadata
    result = result.stdout.strip().split(b"\n")[-1]

    try:
        return json.loads(result)
    except json.JSONDecodeError as ex:
        raise ScarbMetadataFetchException("Failed to decode the metadata json.") from ex


def maybe_fetch_linked_libraries(project_root_path: Path) -> Optional[List[Path]]:
    if not has_scarb_toml(project_root_path):
        logging.info(
            "Scarb.toml not found, using only packages provided by the argument."
        )
        return None

    logging.info("Scarb.toml found, fetching Scarb packages.")

    scarb_toml_path = project_root_path / "Scarb.toml"
    metadata = read_scarb_metadata(scarb_toml_path)

    try:
        # assuming we have only one entry in the workspace section
        current_package_name = metadata["workspace"]["members"][0]

        matching_compilation_units = [
            compilation_unit
            for compilation_unit in metadata["compilation_units"]
            if compilation_unit["package"] == current_package_name
        ]

        matching_contract_units = [
            compilation_unit
            for compilation_unit in matching_compilation_units
            if compilation_unit["target"]["kind"] == "starknet-contract"
        ]
        matching_lib_units = [
            compilation_unit
            for compilation_unit in matching_compilation_units
            if compilation_unit["target"]["kind"] == "lib"
        ]

        # if contract target does not exist we fall back to lib
        unit_with_dependencies = (
            matching_contract_units[0]
            if matching_contract_units
            else matching_lib_units[0]
        )

        if len(matching_contract_units) > 1:
            logging.warning(
                "Scarb found multiple starknet-contract targets - using the target named %s.",
                {unit_with_dependencies["target"]["name"]},
            )

        valuable_dependencies = filter(
            lambda dependency: dependency["name"] != "core",
            unit_with_dependencies["components_data"],
        )

        paths: List[Path] = list(
            map(
                lambda component: find_directory_with_cairo_project_toml(
                    Path(component["source_path"])
                ),
                valuable_dependencies,
            )
        )

    except (IndexError, KeyError) as ex:
        raise ScarbMetadataFetchException("Error parsing metadata:\n" + str(ex)) from ex

    return paths


def find_directory_with_cairo_project_toml(lib_cairo_path: Path) -> Path:
    src_directory_path = lib_cairo_path.parent
    return (
        src_directory_path
        if "cairo_project.toml" in os.listdir(src_directory_path)
        else src_directory_path.parent
    )
