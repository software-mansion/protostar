# pyright: reportUnknownLambdaType=false
from typing import Optional, Dict, Tuple
from pathlib import Path
import os
import json
import shutil
import subprocess

import logging

from protostar.protostar_exception import ProtostarException


class ScarbMetadataFetchException(ProtostarException):
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(
            "Error while trying to fetch Scarb metadata:\n" + message, details
        )


def read_scarb_metadata(scarb_toml_path: Path) -> Dict:
    scarb_path = shutil.which("scarb")
    if not scarb_path:
        raise ProtostarException(
            "Scarb not found. "
            "Install Scarb from https://docs.swmansion.com/scarb/download "
            "and use it to manage your dependencies."
            # TODO #1957
        )

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


def fetch_linked_libraries_from_scarb(
    package_root_path: Path,
) -> list[Tuple[Path, str]]:
    if "Scarb.toml" not in os.listdir(package_root_path):
        raise ProtostarException(
            "Scarb.toml not found. Please make sure to manage your dependencies using Scarb."
            # TODO #1957
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

        valuable_dependencies = [
            dependency
            for dependency in unit_with_dependencies["components_data"]
            if dependency["name"] != "core"
        ]

        paths_and_package_names: list[Tuple[Path, str]] = [
            (
                validate_path_exists_and_return_source_root(
                    Path(component["source_path"])
                ),
                component["name"],
            )
            for component in valuable_dependencies
        ]

    except (IndexError, KeyError) as ex:
        raise ScarbMetadataFetchException("Error parsing metadata:\n" + str(ex)) from ex

    return paths_and_package_names


def validate_path_exists_and_return_source_root(lib_cairo_path: Path) -> Path:
    if not lib_cairo_path.exists():
        raise ProtostarException(
            "The file "
            + str(lib_cairo_path)
            + " is expected by Scarb, but it does not exist."
            # TODO #1957
        )
    return lib_cairo_path.parent
