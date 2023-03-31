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
            check=False,  # don't throw exception on fail
            cwd=scarb_toml_path,
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
    result = result.stdout.decode("utf-8").strip().split("\n")[-1]

    try:
        return json.loads(result)
    except json.JSONDecodeError as ex:
        raise ScarbMetadataFetchException("Failed to decode metadata json.") from ex


def maybe_fetch_linked_libraries(project_root_path: Path) -> Optional[List[Path]]:
    if not has_scarb_toml(project_root_path):
        logging.info(
            "Scarb.toml not found, using only packages provided by the argument."
        )
        return None

    logging.info("Scarb.toml found, fetching Scarb packages.")

    scarb_toml_path = project_root_path / "Scarb.toml"
    metadata = read_scarb_metadata(scarb_toml_path)

    paths: List[Path] = []

    try:
        # is this reliable?
        comp_unit_idx = 0
        current_package_name = metadata["compilation_units"][comp_unit_idx]["package"]

        for package in metadata["compilation_units"][comp_unit_idx]["components_data"]:
            if package["name"] == "core":
                continue

            if package["name"] == current_package_name:
                continue

            paths.append(package["source_path"])

    except (IndexError, KeyError) as ex:
        raise ScarbMetadataFetchException("Error parsing metadata:\n" + str(ex)) from ex

    return paths
