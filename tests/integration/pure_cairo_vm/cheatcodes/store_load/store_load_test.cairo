from starkware.cairo.common.math import assert_not_zero

func test_store_load_simple() {
    alloc_locals;
    local x;
    local y;

    %{
        ids.x = 12
        store("x", ids.x)
    %}
    %{
        ids.y = load("x")
    %}
    assert y = x;
    return ();
}
