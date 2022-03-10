def inject_protostar_hint_locals(fn_run_from_entrypoint, test_runner):
    def modified_run_from_entrypoint(
        *args,
        **kwargs,
    ):
        if "hint_locals" in kwargs and kwargs["hint_locals"] is not None:
            kwargs["hint_locals"]["__test_runner"] = test_runner
        return fn_run_from_entrypoint(
            *args,
            **kwargs,
        )

    return modified_run_from_entrypoint
