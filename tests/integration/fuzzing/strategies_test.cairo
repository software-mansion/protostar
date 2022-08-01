%lang starknet

from starkware.cairo.common.math import assert_nn

@external
func test_unknown_parameter{syscall_ptr : felt*, range_check_ptr}(a : felt):
    %{
        given(
            a = st.signed(),
            b = st.integers(min=100, max=200),
        )
    %}
    return ()
end

@external
func test_not_strategy_object{syscall_ptr : felt*, range_check_ptr}(a : felt, b : felt):
    %{
        given(a = [])
    %}
    return ()
end
