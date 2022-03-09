def curry_run_from_entrypoint(fn, test_runner):
    def curried_run_from_entrypoint(
        *args,
        **kwargs,
    ):
        kwargs["hint_locals"] = {"__test_runner": test_runner}
        return fn(
            *args,
            **kwargs,
        )

    return curried_run_from_entrypoint
