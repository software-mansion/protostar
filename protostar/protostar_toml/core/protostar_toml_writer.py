from pathlib import Path
from typing import List, OrderedDict

import tomli_w

from protostar.protostar_toml.core.protostar_toml_section import ProtostarTOMLSection
from protostar.protostar_toml.protostar_config import ProtostarConfig
from protostar.protostar_toml.protostar_contracts import ProtostarContracts
from protostar.protostar_toml.protostar_project import ProtostarProject


class ProtostarTOMLWriter:
    # pylint: disable=no-self-use
    def save(
        self,
        path: Path,
        protostar_config: ProtostarConfig,
        protostar_project: ProtostarProject,
        protostar_contracts: ProtostarContracts,
    ) -> None:
        result = OrderedDict()

        sections: List[ProtostarTOMLSection] = [
            protostar_config,
            protostar_project,
            protostar_contracts,
        ]

        for section in sections:
            result[section.get_section_name()] = section.to_dict()

        with open(path, "wb") as protostar_toml_file:
            tomli_w.dump(result, protostar_toml_file)
