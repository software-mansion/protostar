func test_syscall_deployment_abi_storing() {
    alloc_locals;
    local deployer_address;

    %{
        ids.deployer_address = deploy_contract("deployer").ok.contract_address
        declared = declare("block_number_contract").ok
        invoke(ids.deployer_address, "deploy_contract", [declared.class_hash])
        deployed_address = call(ids.deployer_address, "get_deployed_contract_address").ok[0]

        stored_value = [5, 10]

        store(deployed_address, "target_map_struct_val", stored_value, key=[1])
        loaded_value = load(deployed_address, "target_map_struct_val", "Value", key=[1]).ok

        assert loaded_value == stored_value, f"Loaded value is not correct, got {loaded_value}"
    %}
    return ();
}
