fn test_deploy_tp_cairo0() {
    let mut arr = ArrayTrait::new();
    arr.append(1);
    arr.append(2);
    match deploy_tp_cairo0(123, 123, arr) {
        Result::Ok(deployed_contract_address) => (),
        Result::Err(x) => {
            let mut data = array_new::<felt>();
            array_append::<felt>(ref data, x);
            panic(data)
        },
    }
}

fn test_deploy_cairo0() {
    let mut arr = ArrayTrait::new();
    arr.append(1);
    arr.append(2);
    arr.append(3);
    match deploy_cairo0(
        PreparedContract { contract_address: 123, class_hash: 123, constructor_calldata: arr }
    ) {
        Result::Ok(deployed_contract_address) => (),
        Result::Err(x) => {
            let mut data = array_new::<felt>();
            array_append::<felt>(ref data, x);
            panic(data)
        },
    }
}
