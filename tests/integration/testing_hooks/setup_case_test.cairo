%lang starknet

@external
func __setup__():
    %{ context.setup_hook_executed = "yes" %}
    return ()
end

@external
func setup_setup_case():
    %{ context.setup_case_executed = "yes" %}
    %{ assert context.setup_hook_executed == "yes" %}
    return ()
end

@external
func test_setup_case():
    %{ assert context.setup_hook_executed == "yes" %}
    %{ assert context.setup_case_executed == "yes" %}

    return ()
end

@external
func test_setup_hook_only():
    %{ assert context.setup_hook_executed == "yes" %}
    %{ assert not hasattr(context, "setup_case_executed") %}

    return ()
end


@external
func setup_setup_case_fails():
    %{ assert False %}
    return ()
end

@external
func test_setup_case_fails():
    return ()
end
