from pathlib import Path

import pytest
from starkware.cairo.lang.compiler.preprocessor.preprocessor import PreprocessedProgram

from .cairo_compiler import CairoCompiler
from .compiler_config import CompilerConfig

EXAMPLES_DIR_PATH = Path(__file__).parent / "cairo_compiler"


@pytest.mark.parametrize(
    "test_file, test_function",
    (
        (EXAMPLES_DIR_PATH / "array_sum_test.cairo", "test_array_sum"),
        (
            EXAMPLES_DIR_PATH / "array_sum_external_test.cairo",
            "test_array_sum_external",
        ),
    ),
)
def test_compilation(test_file: Path, test_function: str):
    config = CompilerConfig(
        include_paths=[str(EXAMPLES_DIR_PATH)], disable_hint_validation=False
    )
    compiler = CairoCompiler(config)

    preprocessed = compiler.preprocess(test_file)
    assert isinstance(preprocessed, PreprocessedProgram)

    compiled = compiler.compile_preprocessed(preprocessed)
    assert test_function in compiled.identifiers.root.identifiers.keys()
