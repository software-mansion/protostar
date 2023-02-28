from starkware.cairo.common.math import assert_not_zero

func test_warp(){
    alloc_locals;
    local deployed_contract_address;

    %{
        ids.deployed_contract_address = deploy_contract("./src/main.cairo").ok.contract_address
        assert warp(ids.deployed_contract_address, 123).err_code == 0
    %}

    assert_not_zero(deployed_contract_address);

    local stored_block_timestamp;
    %{
        ids.stored_block_timestamp = call(ids.deployed_contract_address, "get_syscall_block_timestamp").ok[0]
    %}

    assert stored_block_timestamp = 123;

    return ();
}

func test_warp_with_invoke(){
    alloc_locals;
    local deployed_contract_address;

    %{
        ids.deployed_contract_address = deploy_contract("./src/main.cairo").ok.contract_address
        assert warp(ids.deployed_contract_address, 123).err_code == 0
    %}

    assert_not_zero(deployed_contract_address);

    // Set the storage variable stored_block_timestamp to warped value
    %{ assert invoke(ids.deployed_contract_address, "set_stored_block_timestamp_to_syscall_value").err_code == 0 %}

    // Retrieve the stored value
    local stored_block_timestamp;
    %{ ids.stored_block_timestamp = call(ids.deployed_contract_address, "get_stored_block_timestamp").ok[0] %}
    assert stored_block_timestamp = 123;

    return ();
}

// warp contract B, invoke contract A, A calls B, B asserts it's warped
func test_warp_with_invoke_depth_2(){
    alloc_locals;
    local deployed_contract_address_A;
    local deployed_contract_address_B;

    %{
        ids.deployed_contract_address_A = deploy_contract("./src/main.cairo").ok.contract_address
        ids.deployed_contract_address_B = deploy_contract("./src/main.cairo").ok.contract_address
        assert warp(ids.deployed_contract_address_B, 123).err_code == 0
    %}

    assert_not_zero(deployed_contract_address_A);
    assert_not_zero(deployed_contract_address_B);

    // Set the storage variable stored_block_timestamp of contract B to warped value
    %{ assert invoke(ids.deployed_contract_address_A, "invoke_set_stored_block_timestamp_to_syscall_value",
       [ids.deployed_contract_address_B]).err_code == 0 %}

    // Retrieve the stored value from contract B
    local stored_block_timestamp_B;
    %{ ids.stored_block_timestamp_B = call(ids.deployed_contract_address_B, "get_stored_block_timestamp").ok[0] %}
    assert stored_block_timestamp_B = 123;

    return ();
}
