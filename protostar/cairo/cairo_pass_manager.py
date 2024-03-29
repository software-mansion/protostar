from starkware.cairo.lang.cairo_constants import DEFAULT_PRIME
from starkware.cairo.lang.compiler.cairo_compile import get_module_reader
from starkware.cairo.lang.compiler.preprocessor.pass_manager import PassManager
from starkware.cairo.lang.compiler.preprocessor.default_pass_manager import (
    default_pass_manager,
)

from .pass_manager import PassManagerConfig, PassManagerFactory


class CairoPassManagerFactory(PassManagerFactory):
    @staticmethod
    def build(config: PassManagerConfig) -> PassManager:
        read_module = get_module_reader(cairo_path=config.include_paths).read
        return default_pass_manager(
            prime=DEFAULT_PRIME,
            read_module=read_module,
        )
