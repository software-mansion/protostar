struct Key {
    a: felt,
    b: felt,
}

struct Value {
    a: felt,
    b: felt,
}


func test_load() {
    alloc_locals;
    local contract_address;
    local value;
    local bn;

    %{
        ids.contract_address = deploy_contract("block_number_contract").ok.contract_address
        store(ids.contract_address, "target", [5])
        ids.value = load(ids.contract_address, "target", "felt").ok[0]
        ids.bn = call(ids.contract_address, "get_value").ok[0]
    %}

    assert bn = value;
    return ();
}

func test_load_map() {
    alloc_locals;
    local contract_address;
    local value;
    local bn;

    %{
        ids.contract_address = deploy_contract("block_number_contract").ok.contract_address
        store(ids.contract_address, "target_map", [5], key=[12])
        ids.value = load(ids.contract_address, "target_map", "felt", key=[12]).ok[0]
        ids.bn = call(ids.contract_address, "get_map_value", [12]).ok[0]
    %}

    assert bn = value;
    return ();
}

func test_load_map_complex_key() {
    alloc_locals;
    local contract_address;
    local value;
    local bn;

    %{
        ids.contract_address = deploy_contract("block_number_contract").ok.contract_address
        store(ids.contract_address, "target_map_complex_key", [5], key=[1,2])
        ids.value = load(ids.contract_address, "target_map_complex_key", "felt", key=[1,2]).ok[0]
        ids.bn = call(ids.contract_address, "get_map_value_complex_key", [1,2]).ok[0]
    %}

    assert bn = 5;
    return ();
}

func test_load_map_struct_key() {
    alloc_locals;
    local contract_address;
    local value;
    local bn;

    %{
        ids.contract_address = deploy_contract("block_number_contract").ok.contract_address
        store(ids.contract_address, "target_map_struct_key", [5], key=[1,2])
        ids.value = load(ids.contract_address, "target_map_struct_key", "felt", key=[1,2]).ok[0]
        ids.bn = call(ids.contract_address, "get_map_value_struct_key", [1,2]).ok[0]
    %}

    assert bn = value;

    return ();
}

func test_load_map_struct_val() {
    alloc_locals;
    local contract_address;
    local value: Value;

    local bn: Value;
    %{
        ids.contract_address = deploy_contract("block_number_contract").ok.contract_address
        store(ids.contract_address, "target_map_struct_val", [5,10], key=[1])
        value_arr = load(ids.contract_address, "target_map_struct_val", "Value", key=[1]).ok
        ids.value.a, ids.value.b = value_arr

        call_result = call(ids.contract_address, "get_map_value_struct_val", [1]).ok
        ids.bn.a, ids.bn.b = call_result
    %}

    assert value.a = bn.a;
    assert value.b = bn.b;
    return ();
}

func test_missing_type_name() {
    alloc_locals;
    local contract_address;
    // assert in load_test.py
    local value: Value;
    %{
        ids.contract_address = deploy_contract("block_number_contract").ok.contract_address
        store(ids.contract_address, "target_map_complex_key", [1, 2], key=[5, 6])
        value_arr = load(ids.contract_address, "target_map_complex_key", "ValueB", key=[5,6])
    %}
    return ();
}

func test_loading_from_contract_deployed_by_syscall() {
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
