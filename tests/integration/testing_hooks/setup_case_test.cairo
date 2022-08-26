%lang starknet
from starkware.cairo.common.cairo_builtins import HashBuiltin

@external
func __setup__():
    %{ context.setup_hook_executed = "yes" %}
    return ()
end

@external
func setup_setup_hooks():
    %{ context.setup_case_executed = "yes" %}
    %{ assert context.setup_hook_executed == "yes" %}
    return ()
end

@external
func test_setup_hooks{
    syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr
}():
    %{ assert context.setup_hook_executed == "yes" %}
    %{ assert context.setup_case_executed == "yes" %}

    return ()
end
