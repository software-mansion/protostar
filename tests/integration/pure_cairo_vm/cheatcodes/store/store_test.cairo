struct Key {
    a: felt,
    b: felt,
}

struct Value {
    a: felt,
    b: felt,
}

func test_store() {
    alloc_locals;
    local contract_address;
    local bn;

    %{
        ids.contract_address = deploy_contract("block_number_contract").ok.contract_address
        store(ids.contract_address, "target", [5])
        ids.bn = call(ids.contract_address, "get_value").ok[0]
    %}

    assert bn = 5;
    return ();
}

func test_store_map() {
    alloc_locals;
    local contract_address;
    local bn;

    %{
        ids.contract_address = deploy_contract("block_number_contract").ok.contract_address
        store(ids.contract_address, "target_map", [5], key=[12])
        ids.bn = call(ids.contract_address, "get_map_value", [12]).ok[0]
    %}

    assert bn = 5;
    return ();
}

func test_store_map_complex_key() {
    alloc_locals;
    local contract_address;
    local bn;

    %{
        ids.contract_address = deploy_contract("block_number_contract").ok.contract_address
        store(ids.contract_address, "target_map_complex_key", [5], key=[1,2])
        ids.bn = call(ids.contract_address, "get_map_value_complex_key", [1, 2]).ok[0]
    %}

    assert bn = 5;
    return ();
}


func test_store_map_struct_val() {
    alloc_locals;
    local contract_address;
    local bn: Value;

    %{
        ids.contract_address = deploy_contract("block_number_contract").ok.contract_address
        store(ids.contract_address, "target_map_struct_val", [5,10], key=[1])
        result = call(ids.contract_address, "get_map_value_struct_val", [1]).ok
        ids.bn.a = result[0]
        ids.bn.b = result[1]
    %}

    assert 5 = bn.a;
    assert 10 = bn.b;
    return ();
}
