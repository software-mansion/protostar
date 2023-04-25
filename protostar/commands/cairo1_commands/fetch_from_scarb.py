# pyright: reportUnknownLambdaType=false
from typing import Optional, Dict
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


def has_scarb_toml(package_root_path: Path) -> bool:
    return "Scarb.toml" in os.listdir(package_root_path)


def read_scarb_metadata(scarb_toml_path: Path) -> Dict:
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

    if result.returncode != 0:
        raise ScarbMetadataFetchException(
            "Metadata fetch returned a non-zero exit code. "
            'Try running "scarb metadata --format-version 1" to diagnose the problem.'
        )

    # only the last line of the output contains metadata
    result = result.stdout.strip().split(b"\n")[-1]

    try:
        return json.loads(result)
    except json.JSONDecodeError as ex:
        raise ScarbMetadataFetchException(
            "Failed to decode the metadata json. "
            'Try running "scarb metadata --format-version 1" to diagnose the problem.'
        ) from ex


def maybe_fetch_linked_libraries_from_scarb(
    package_root_path: Path, linked_libraries: list[Path]
) -> list[Path]:
    if not package_root_path.is_dir() or not has_scarb_toml(package_root_path):
        return []

    if linked_libraries:
        raise ProtostarException(
            "Provided linked-libraries (explicitly or in protostar.toml) while Scarb.toml was present. "
            "Manage all of your dependencies using Scarb."
        )

    scarb_toml_path = package_root_path / "Scarb.toml"
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
                unit_with_dependencies["target"]["name"],
            )

        valuable_dependencies = filter(
            lambda dependency: dependency["name"] != "core",
            unit_with_dependencies["components_data"],
        )

        paths: list[Path] = list(
            map(
                lambda component: validate_path_exists_and_find_directory_with_config(
                    Path(component["source_path"])
                ),
                valuable_dependencies,
            )
        )

        if len(paths) != len(set(paths)):
            raise ProtostarException(
                "At least one cairo_project.toml is shared between packages. "
                "Make sure every package has its own cairo_project.toml"
            )

    except (IndexError, KeyError) as ex:
        raise ScarbMetadataFetchException("Error parsing metadata:\n" + str(ex)) from ex

    return paths


def validate_path_exists_and_find_directory_with_config(lib_cairo_path: Path) -> Path:
    if not lib_cairo_path.exists():
        raise ProtostarException(
            "The file "
            + str(lib_cairo_path)
            + " is expected by Scarb, but it does not exist."
        )

    src_directory_path = lib_cairo_path.parent
    result = (
        src_directory_path
        if "cairo_project.toml" in os.listdir(src_directory_path)
        else src_directory_path.parent
    )

    if "cairo_project.toml" not in os.listdir(result):
        raise ProtostarException(
            "Missing cairo_project.toml for package located in "
            + str(src_directory_path.parent)
        )

    return result
