from starkware.cairo.common.math import assert_not_zero

func test_deploying_pipeline_with_path(){
    alloc_locals;
    local declared_class;
    local deployed_hash;

    %{
        declared = declare("./src/main.cairo")
        ids.declared_class = declared.class_hash
        prepared = prepare(declared)
        deployed = deploy(prepared)
        ids.deployed_hash = deployed.contract_address
    %}

    assert_not_zero(declared_class);
    assert_not_zero(deployed_hash);

    return ();
}

func test_deploying_pipeline(){
    alloc_locals;
    local declared_class;
    local deployed_hash;

    %{
        declared = declare("main")
        ids.declared_class = declared.class_hash
        prepared = prepare(declared)
        deployed = deploy(prepared)
        ids.deployed_hash = deployed.contract_address
    %}

    assert_not_zero(declared_class);
    assert_not_zero(deployed_hash);

    return ();
}

func test_two_interleaving_flows(){
    alloc_locals;
    local declared_class_1;
    local declared_class_2;

    local deployed_hash_1;
    local deployed_hash_2;

    %{
        declared_1 = declare("main")
        declared_2 = declare("main")

        ids.declared_class_1 = declared_1.class_hash
        ids.declared_class_2 = declared_2.class_hash

        prepared_1 = prepare(declared_1)
        prepared_2 = prepare(declared_2)

        deployed_1 = deploy(prepared_1)
        ids.deployed_hash_1 = deployed_1.contract_address

        deployed_2 = deploy(prepared_2)
        ids.deployed_hash_2 = deployed_2.contract_address

    %}

    assert_not_zero(declared_class_1);
    assert_not_zero(declared_class_2);
    assert_not_zero(deployed_hash_1);
    assert_not_zero(deployed_hash_2);

    return ();
}