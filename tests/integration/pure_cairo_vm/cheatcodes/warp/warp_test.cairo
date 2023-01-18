from starkware.cairo.common.math import assert_not_zero

func test_warp(){
    alloc_locals;
    local deployed_contract_address;

    %{
        ids.deployed_contract_address = deploy_contract("./src/main.cairo").contract_address
        warp(ids.deployed_contract_address, 123)
    %}

    assert_not_zero(deployed_contract_address);

    local timestamp;
    %{
        ids.timestamp = call(ids.deployed_contract_address, "timestamp_getter")[0]
    %}

    assert timestamp = 123;
    return ();
}

func test_warp_with_invoke(){
    alloc_locals;
    local deployed_contract_address;

    %{
        ids.deployed_contract_address = deploy_contract("./src/main.cairo").contract_address
        warp(ids.deployed_contract_address, 123)
    %}
    assert_not_zero(deployed_contract_address);

    // Set the timestamp to rolled value
    %{ invoke(ids.deployed_contract_address, "block_timestamp_setter") %}

    // Retrieve stored value
    local stored_block_timestamp;
    %{ ids.stored_block_timestamp = call(ids.deployed_contract_address, "stored_block_timestamp_getter")[0] %}
    assert stored_block_timestamp = 123;
    return ();
}