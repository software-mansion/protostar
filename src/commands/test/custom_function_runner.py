from starkware.cairo.common.cairo_function_runner import CairoFunctionRunner


class CustomCairoFunctionRunner(CairoFunctionRunner):
    text_execution_env = None

    def run_from_entrypoint(self, *args, **kwargs):
        if "hint_locals" in kwargs and kwargs["hint_locals"] is not None:
            kwargs["hint_locals"]["test_env"] = self.text_execution_env
        super().run_from_entrypoint(*args, **kwargs)
