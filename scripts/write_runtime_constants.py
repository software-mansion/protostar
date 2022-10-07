import json
from pathlib import Path
import tomli
from starkware.cairo.lang.version import __version__ as cairo_v

from protostar.self.protostar_directory import ProtostarDirectory, RuntimeConstantsDict

script_path = Path(__file__)
project_root = Path(script_path).parent.parent

raw_pyproject = (project_root / "pyproject.toml").read_text("utf-8")
pyproject = tomli.loads(raw_pyproject)
protostar_v = pyproject["tool"]["poetry"]["version"]

RUNTIME_CONSTANTS: RuntimeConstantsDict = {
    "PROTOSTAR_VERSION": protostar_v,
    "CAIRO_VERSION": cairo_v,
}

(project_root / ProtostarDirectory.RUNTIME_CONSTANTS_FILE_NAME).write_text(
    json.dumps(RUNTIME_CONSTANTS, indent=4),
    encoding="utf-8",
)
