from pathlib import Path

from docs_generator import ReferenceDocsGenerator
from src.protostar_cli import ProtostarCLI

CLI_REFERENCE_MARKDOWN_CONTENT = ReferenceDocsGenerator(
    ProtostarCLI.create(Path())
).generate_cli_reference_markdown()
ReferenceDocsGenerator.save_to_markdown_file(
    Path(__file__).parent / ".." / "website/docs/cli-reference.md",
    CLI_REFERENCE_MARKDOWN_CONTENT,
)
