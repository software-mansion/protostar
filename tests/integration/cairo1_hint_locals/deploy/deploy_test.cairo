use array::ArrayTrait;

#[test]
fn test_deploy() {
    match declare('minimal') {
        Result::Ok(class_hash) => {
            assert(class_hash != 0, 'class_hash != 0');
            let mut constructor_calldata = ArrayTrait::new();
            constructor_calldata.append(1);
            constructor_calldata.append(2);
            constructor_calldata.append(3);
            let x = PreparedContract {contract_address: 123, class_hash: 123, constructor_calldata: constructor_calldata};
            deploy(x);
        },
        Result::Err(x) => {
            let mut data = ArrayTrait::new();
            data.append(x);
            panic(data)
        },
    }
}

