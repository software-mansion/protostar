from starkware.cairo.common.math import assert_not_zero, assert_not_equal

func test_stop_warp(){
    alloc_locals;
    local deployed_contract_address;

    %{
        ids.deployed_contract_address = deploy_contract("./src/main.cairo").ok.contract_address
        assert warp(ids.deployed_contract_address, 123).err_code == 0
    %}

    assert_not_zero(deployed_contract_address);

    local timestamp;
    %{
        ids.timestamp = call(ids.deployed_contract_address, "get_syscall_block_timestamp").ok[0]
    %}

    assert timestamp = 123;

    %{
        assert stop_warp(ids.deployed_contract_address).err_code == 0
    %}

    local timestamp_after_stopping;
    %{
        ids.timestamp_after_stopping = call(ids.deployed_contract_address, "get_syscall_block_timestamp").ok[0]
    %}

    assert_not_equal(timestamp_after_stopping, 123);

    return ();
}

func test_stop_warp_with_invoke(){
    alloc_locals;
    local deployed_contract_address;

    %{
        ids.deployed_contract_address = deploy_contract("./src/main.cairo").ok.contract_address
        assert warp(ids.deployed_contract_address, 123).err_code == 0
    %}
    assert_not_zero(deployed_contract_address);

    %{ assert invoke(ids.deployed_contract_address, "set_stored_block_timestamp_to_syscall_value").err_code == 0 %}

    local stored_block_timestamp;
    %{ ids.stored_block_timestamp = call(ids.deployed_contract_address, "get_stored_block_timestamp").ok[0] %}
    assert stored_block_timestamp = 123;

    local stored_timestamp_after_stopping;
    %{
        assert stop_warp(ids.deployed_contract_address).err_code == 0
        assert invoke(ids.deployed_contract_address, "set_stored_block_timestamp_to_syscall_value").err_code == 0
        ids.stored_timestamp_after_stopping = call(ids.deployed_contract_address, "get_stored_block_timestamp").ok[0]
    %}

    assert_not_equal(stored_timestamp_after_stopping, 123);

    return ();
}
