func test_declaring_contract(){
    alloc_locals;
    local declared_class;

    %{ ids.declared_class = declare("main").class_hash %}
    assert declared_class = 3486615995825404773763675912942359106768738718722212119221423115555603404330;
    return ();
}