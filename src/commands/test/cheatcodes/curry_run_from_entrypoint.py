def curry_run_from_entrypoint(fn, test_runner):
    def curried_run_from_entrypoint(
        *args,
        **kwargs,
    ):
        if "hint_locals" in kwargs and kwargs["hint_locals"] is not None:
            kwargs["hint_locals"]["__test_runner"] = test_runner
        return fn(
            *args,
            **kwargs,
        )

    return curried_run_from_entrypoint
