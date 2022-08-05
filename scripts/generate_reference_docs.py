from pathlib import Path

from docs_generator import ReferenceDocsGenerator
from protostar.composition_root import build_di_container

CLI_REFERENCE_MARKDOWN_CONTENT = ReferenceDocsGenerator(
    build_di_container(Path()).protostar_cli
).generate_cli_reference_markdown()

ReferenceDocsGenerator.save_to_markdown_file(
    Path(__file__).parent.parent / "website/docs/cli-reference.md",
    CLI_REFERENCE_MARKDOWN_CONTENT,
)
