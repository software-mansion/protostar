from starkware.cairo.common.math import assert_not_zero

func test_call_unknown_fail() {
    alloc_locals;
    %{
        addr = deploy_contract("./src/basic.cairo").contract_address
        result = call(addr, "get_balance")
        assert result == [100]
    %}
    %{
        addr = deploy_contract("basic").contract_address
        result = call(addr, "get_balance")
        assert result == [100]
    %}
    return ();
}
