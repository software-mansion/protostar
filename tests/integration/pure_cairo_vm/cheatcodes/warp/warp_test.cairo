from starkware.cairo.common.math import assert_not_zero

func test_warp_works() {
    %{
        contract_address = deploy_contract("tests/integration/pure_cairo_vm/cheatcodes/warp/timestamp_contract.cairo").contract_address

        warp(123, contract_address)
        result = call(contract_address, "get_timestamp")

        assert result == [123], f"{result}"
    %}
    return ();
}
