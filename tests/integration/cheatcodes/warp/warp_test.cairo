%lang starknet

from starkware.starknet.common.syscalls import get_block_timestamp

@view
func test_changing_timestamp{syscall_ptr : felt*}():
    %{ stop_warp = warp(321) %}
    let (bt) = get_block_timestamp()
    assert bt = 321

    %{ stop_warp() %}
    let (bt2) = get_block_timestamp()
    %{ assert ids.bt2 != 321 %}
    return ()
end

@contract_interface
namespace TimestampContract:
    func get_timestamp() -> (res : felt):
    end
end

@view
func test_changing_timestamp_in_deployed_contract{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals
    local contract_address

    %{ ids.contract_address = deploy_contract("./tests/integration/cheatcodes/warp/timestamp_contract.cairo").contract_address %}
    let (initial_timestamp) = TimestampContract.get_timestamp(contract_address)

    %{ stop_warp = warp(321, ids.contract_address) %}
    let (timestamp) = TimestampContract.get_timestamp(contract_address)
    assert timestamp = 321
    let (local_timestamp) = get_block_timestamp()
    %{
        assert ids.local_timestamp != 321
        stop_warp()
    %}

    let (timestamp2) = TimestampContract.get_timestamp(contract_address)

    %{ assert ids.timestamp != ids.timestamp2 %}

    return ()
end
