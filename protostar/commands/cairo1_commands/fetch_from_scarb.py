from typing import Optional, Dict
from pathlib import Path
import os

import json
import subprocess

from protostar.protostar_exception import ProtostarException


def has_scarb_toml(project_root_path: Path) -> bool:
    return "Scarb.toml" in os.listdir(project_root_path)


# /// Reads Scarb project metadata from manifest file.
# read_scarb_me
# fn read_scarb_metadata(manifest_path: PathBuf) -> anyhow::Result<ScarbProjectMetadata> {
#     let mut cmd = Command::new("scarb");
#     cmd.args(["--json", "-vv", "metadata", "--format-version=1"]);
#     cmd.stdout(Stdio::piped());
#     cmd.current_dir(manifest_path.parent().unwrap());
#     let output = cmd.output()?;

#     let slice = output.stdout.as_slice();
#     slice
#         .lines()
#         .flat_map(anyhow::Result::ok)
#         .flat_map(|line| serde_json::from_str::<ScarbProjectMetadata>(&line).ok())
#         .next()
#         .ok_or_else(|| {
#             anyhow!(
#                 indoc! {r#"
#                 Scarb.toml not found. Calling `scarb metadata` failed.
#                 stderr:
#                 {}"#},
#                 String::from_utf8_lossy(&output.stderr)
#             )
#         })
# }


class ScarbMetadataFetchException(ProtostarException):
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(
            "Error while trying to fetch Scarb metadata:\n" + message, details
        )


def read_scarb_metadata(scarb_toml_path: Path) -> Dict:
    try:
        subprocess.run(
            ["scarb --json -vv metadata --format-version=1"],
            check=False,  # dont throw exception on fail
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

    result = result.stdout.decode("utf-8").strip()

    try:
        return json.loads(result)
    except json.JSONDecodeError as ex:
        raise ScarbMetadataFetchException("Failed to load metadata json.")


def maybe_fetch_linked_libraries(project_root_path: Path) -> Optional[...]:

    if not has_scarb_toml(project_root_path):
        return None

    scarb_toml_path = project_root_path / "Scarb.toml"
    metadata = read_scarb_metadata(scarb_toml_path)

    print(metadata)
