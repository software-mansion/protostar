from .generate_command_input_types import (
    OUTPUT_PATH,
    create_module_construct,
    generate_code,
)


def test_input_types_are_up_to_date():
    module_construct = create_module_construct()

    result = generate_code(module_construct)

    assert (
        result == OUTPUT_PATH.read_text()
    ), "It looks like generated types are outdated. Run `poe codegen`."
