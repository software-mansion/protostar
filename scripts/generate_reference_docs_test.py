from pathlib import Path

from docs_generator.reference_docs_generator import ReferenceDocsGenerator
from protostar.composition_root import build_di_container


def test_instance_matches_cli_reference_docs():
    di_container = build_di_container(script_root=Path(), cwd=Path())
    new_snapshot = ReferenceDocsGenerator(
        di_container.protostar_cli
    ).generate_cli_reference_markdown()

    with open(
        Path(__file__).parent.parent / "website" / "docs" / "cli-reference.md",
        "r",
        encoding="utf-8",
    ) as doc_file:
        snapshot = doc_file.read()

        assert snapshot == new_snapshot, "Snapshot mismatch. Run `poe update_cli_docs`."
