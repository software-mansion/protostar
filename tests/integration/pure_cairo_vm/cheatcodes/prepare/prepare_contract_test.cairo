from starkware.cairo.common.math import assert_not_zero

func test_preparing_deployment_no_constructor(){
    alloc_locals;
    local contract_address;
    local class_hash;
    local salt;

    %{
        declared = declare("./src/basic_no_constructor.cairo").unwrap()
        prepared = prepare(declared).unwrap()

        ids.contract_address = prepared.contract_address
        ids.class_hash = prepared.class_hash
        ids.salt = prepared.salt
    %}

    assert_not_zero(contract_address);
    assert_not_zero(class_hash);
    assert_not_zero(salt);


    return ();
}

func test_preparing_deployment_with_constructor_no_args(){
    alloc_locals;
    local contract_address;
    local class_hash;
    local salt;

    %{
        declared = declare("./src/basic_with_constructor_no_args.cairo").unwrap()
        prepared = prepare(declared).unwrap()

        ids.contract_address = prepared.contract_address
        ids.class_hash = prepared.class_hash
        ids.salt = prepared.salt
    %}

    assert_not_zero(contract_address);
    assert_not_zero(class_hash);
    assert_not_zero(salt);


    return ();
}

func test_preparing_deployment_with_constructor_data_transformer(){
    alloc_locals;
    let initial_balance_input = 1000;
    local initial_balance;

    local contract_address;
    local class_hash;
    local salt;

    // Passing constructor calldata as a dictionary
    %{
        declared = declare("./src/basic_with_constructor.cairo").unwrap()
        prepared = prepare(declared, {"initial_balance": ids.initial_balance_input}).unwrap()
        ids.initial_balance = prepared.constructor_calldata[0]

        ids.contract_address = prepared.contract_address
        ids.class_hash = prepared.class_hash
        ids.salt = prepared.salt
    %}

    assert initial_balance = initial_balance_input;
    assert_not_zero(contract_address);
    assert_not_zero(class_hash);
    assert_not_zero(salt);

    return ();
}


func test_preparing_deployment_with_constructor_no_data_transformer(){
    alloc_locals;
    let initial_balance_input = 1000;
    local initial_balance;

    local contract_address;
    local class_hash;
    local salt;

    // Passing constructor calldata as a list
    %{
        declared = declare("./src/basic_with_constructor.cairo").unwrap()
        prepared = prepare(declared, [ids.initial_balance_input]).unwrap()
        ids.initial_balance = prepared.constructor_calldata[0]

        ids.contract_address = prepared.contract_address
        ids.class_hash = prepared.class_hash
        ids.salt = prepared.salt
    %}

    assert initial_balance = initial_balance_input;
    assert_not_zero(contract_address);
    assert_not_zero(class_hash);
    assert_not_zero(salt);

    return ();
}
