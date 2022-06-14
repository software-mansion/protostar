# pylint: disable=no-self-use
from pathlib import Path
from typing import List, Optional, OrderedDict

import tomli_w

from protostar.protostar_toml.protostar_config_section import ProtostarConfigSection
from protostar.protostar_toml.protostar_contracts_section import (
    ProtostarContractsSection,
)
from protostar.protostar_toml.protostar_project_section import ProtostarProjectSection
from protostar.protostar_toml.protostar_toml_section import ProtostarTOMLSection
from protostar.utils.protostar_directory import VersionManager


class ProtostarTOMLWriter:
    def save_default(
        self,
        path: Path,
        version_manager: VersionManager,
        lib_path: Optional[Path] = None,
    ):
        self.save(
            path=path,
            protostar_config=ProtostarConfigSection(
                protostar_version=version_manager.protostar_version
                or VersionManager.parse("0.1.0")
            ),
            protostar_contracts=ProtostarContractsSection(
                contract_name_to_paths={"main": [Path("src/main.cairo")]}
            ),
            protostar_project=ProtostarProjectSection(lib_path or Path("lib")),
        )

    def save(
        self,
        path: Path,
        protostar_config: ProtostarConfigSection,
        protostar_project: ProtostarProjectSection,
        protostar_contracts: ProtostarContractsSection,
    ) -> None:
        result = OrderedDict()

        sections: List[ProtostarTOMLSection] = [
            protostar_config,
            protostar_project,
            protostar_contracts,
        ]

        for section in sections:
            result[f"protostar.{section.get_section_name()}"] = section.to_dict()

        with open(path, "wb") as protostar_toml_file:
            tomli_w.dump(result, protostar_toml_file)
