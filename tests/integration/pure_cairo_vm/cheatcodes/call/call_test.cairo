from starkware.cairo.common.math import assert_not_zero

func test_calling_pipeline(){
    alloc_locals;
    local declared_class;
    local deployed_hash;

    %{
        declared = declare("main")
        ids.declared_class = declared.class_hash
        prepared = prepare(declared)
        deployed = deploy(prepared)
        ids.deployed_hash = deployed.contract_address
        call_result = call(deployed, declared.class_hash, "double_fn", [3])
    %}

    assert_not_zero(declared_class);
    assert_not_zero(deployed_hash);

    return ();
}
