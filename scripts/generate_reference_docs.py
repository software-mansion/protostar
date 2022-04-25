from pathlib import Path

from src.core.reference_docs_generator import ReferenceDocsGenerator
from src.protostar_cli import protostar_cli

CLI_REFERENCE_MARKDOWN_CONTENT = ReferenceDocsGenerator(
    protostar_cli
).generate_cli_reference_markdown()
ReferenceDocsGenerator.save_to_markdown_file(
    Path(__file__).parent / ".." / "website/docs/cli-reference.md",
    CLI_REFERENCE_MARKDOWN_CONTENT,
)
