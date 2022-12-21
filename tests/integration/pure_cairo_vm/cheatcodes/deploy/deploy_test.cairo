func test_deploying_pipeline(){
    alloc_locals;
    local declared_class;
    local deployed_hash;

    %{
        declared = declare("main")
        ids.declared_class = declared.class_hash
        prepared = prepare(declared)
        deployed = deploy(prepared)
    %}
    assert declared_class = 3486615995825404773763675912942359106768738718722212119221423115555603404330;
    assert deployed_hash = 707729449446580710373319759933022535208170098067734019156148963529721784852;

    return ();
}