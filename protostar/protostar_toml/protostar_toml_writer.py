from pathlib import Path
from typing import List, OrderedDict

import tomli_w

from protostar.protostar_toml.protostar_config_section import ProtostarConfigSection
from protostar.protostar_toml.protostar_contracts_section import (
    ProtostarContractsSection,
)
from protostar.protostar_toml.protostar_project_section import ProtostarProjectSection
from protostar.protostar_toml.protostar_toml_section import ProtostarTOMLSection


class ProtostarTOMLWriter:
    # pylint: disable=no-self-use
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
            result[section.get_section_name()] = section.to_dict()

        with open(path, "wb") as protostar_toml_file:
            tomli_w.dump(result, protostar_toml_file)
