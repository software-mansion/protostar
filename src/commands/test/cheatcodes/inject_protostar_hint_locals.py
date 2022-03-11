from src.commands.test.cheatcodes.cheats import (
    ModifiedUnits,
    inject_cheats_into_hint_locals,
)


def inject_protostar_hint_locals(fn_run_from_entrypoint, test_runner):
    def modified_run_from_entrypoint(
        *args,
        **kwargs,
    ):
        if "hint_locals" in kwargs and kwargs["hint_locals"] is not None:
            kwargs["hint_locals"]["__test_runner"] = test_runner
            inject_cheats_into_hint_locals(
                kwargs["hint_locals"],
                modified_units=ModifiedUnits(
                    test_runner=test_runner,
                    cheatable_syscall_handler=kwargs["hint_locals"]["syscall_handler"],
                ),
            )

        return fn_run_from_entrypoint(
            *args,
            **kwargs,
        )

    return modified_run_from_entrypoint
