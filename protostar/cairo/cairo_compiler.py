from dataclasses import dataclass
from pathlib import Path
from typing import List

from starkware.cairo.lang.compiler.assembler import assemble
from starkware.cairo.lang.compiler.preprocessor.preprocessor import PreprocessedProgram
from starkware.cairo.lang.compiler.preprocessor.preprocess_codes import preprocess_codes
from starkware.cairo.lang.compiler.program import Program

from .cairo_pass_manager import CairoPassManagerFactory
from .pass_manager import PassManagerConfig


@dataclass(frozen=True)
class CairoCompilerConfig(PassManagerConfig):
    pass


class CairoCompiler:
    def __init__(self, config: CairoCompilerConfig):
        self.compiler_config = config

    def preprocess(self, file: Path) -> PreprocessedProgram:  # TODO #1280: Cache result
        pass_manager = CairoPassManagerFactory.build(self.compiler_config)
        return preprocess_codes(
            codes=[(file.read_text("utf-8"), str(file))],
            pass_manager=pass_manager,
        )

    @staticmethod
    def compile_preprocessed(
        preprocessed: PreprocessedProgram,
    ) -> Program:  # TODO #1280: Cache result
        return assemble(preprocessed)

    def get_function_names(self, file_path: Path) -> List[str]:
        preprocessed = self.preprocess(file_path)
        return [
            name
            for name, identifier in preprocessed.identifiers.root.identifiers.items()
            if identifier.TYPE == "function"  # pyright: ignore
        ]
