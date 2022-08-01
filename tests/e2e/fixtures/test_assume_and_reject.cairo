%lang starknet

@external
func test_failed_assume_and_reject{syscall_ptr : felt*, range_check_ptr}(a, b):
    if (a - 0) * (a - 1) * (a - 2) * (a - 3) * (a - 4) * (a - 5) == 0:
        %{ reject() %}
        assert 0 = 0
    end

    %{
        assume(ids.b > 2)
    %}

    assert a = b
    return ()
end
