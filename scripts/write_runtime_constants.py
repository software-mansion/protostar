import json
from pathlib import Path
from typing import Union

import tomli
from starkware.cairo.lang.version import __version__ as cairo_v

from protostar.utils.protostar_directory import RuntimeConstant, ProtostarDirectory

script_path = Path(__file__)
project_root = Path(script_path).parent.parent

raw_pyproject = (project_root / "pyproject.toml").read_text("utf-8")
pyproject = tomli.loads(raw_pyproject)
protostar_v = pyproject["tool"]["poetry"]["version"]

RUNTIME_CONSTANTS: dict[RuntimeConstant, Union[str, int]] = {
    "PROTOSTAR_VERSION": protostar_v,
    "CAIRO_VERSION": cairo_v,
}

# dump constants into a json file
with open(
    project_root / ProtostarDirectory.RUNTIME_CONSTANTS_FILE_NAME, mode="w", encoding="utf-8"
) as file:
    constants_json_str = json.dumps(RUNTIME_CONSTANTS, indent=4)
    file.write(constants_json_str)
