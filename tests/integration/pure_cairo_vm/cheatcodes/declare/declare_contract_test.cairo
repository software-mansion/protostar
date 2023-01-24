from starkware.cairo.common.math import assert_not_zero

func test_declaring_contract(){
    alloc_locals;
    local declared_class;

    %{ ids.declared_class = declare("basic").class_hash %}

    assert_not_zero(declared_class);
    return ();
}