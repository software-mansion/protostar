func __setup__(){
    %{
        context.setup_hook_executed = "yes"
    %}

    return ();
}


func test_setup_executed(){
    alloc_locals;
    local setup_suite_executed;
    %{
        ids.setup_suite_executed = 1 if context.setup_hook_executed == "yes" else 0
    %}
    assert setup_suite_executed = 1;
    return ();
}
