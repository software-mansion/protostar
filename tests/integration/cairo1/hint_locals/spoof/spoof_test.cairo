use array::ArrayTrait;
use result::ResultTrait;
use cheatcodes::TxInfoMockTrait;

#[test]
fn test_spoof_transaction_hash() {
    let contract_address = deploy_contract('simple', @ArrayTrait::new()).unwrap();
    let version_before_mock = call(contract_address, 'get_transaction_version', @ArrayTrait::new()).unwrap();

    let mut tx_info = TxInfoMockTrait::default();
    tx_info.transaction_hash = Option::Some(1234);
    start_spoof(contract_address, tx_info);

    invoke(contract_address, 'store_tx_hash', @ArrayTrait::new()).unwrap();
    let return_data = call(contract_address, 'get_stored_tx_hash', @ArrayTrait::new()).unwrap();
    assert(*return_data.at(0_u32) == 1234, *return_data.at(0_u32));

    let return_data = call(contract_address, 'get_transaction_version', @ArrayTrait::new()).unwrap();
    assert(*return_data.at(0_u32) == *version_before_mock.at(0_u32), *return_data.at(0_u32));
}

#[test]
fn test_spoof_tx_info() {
    let contract_address = deploy_contract('simple', @ArrayTrait::new()).unwrap();

    let mut tx_info = TxInfoMockTrait::default();
    tx_info.version = Option::Some(11);
    tx_info.account_contract_address = Option::Some(22);
    tx_info.max_fee = Option::Some(33_u128);
    tx_info.chain_id = Option::Some(44);
    tx_info.nonce = Option::Some(55);
    tx_info.transaction_hash = Option::Some(66);

    let mut signature: Array::<felt252> = ArrayTrait::new();
    signature.append(77);
    signature.append(88);
    tx_info.signature = Option::Some(signature);

    start_spoof(contract_address, tx_info);

    invoke(contract_address, 'store_tx_hash', @ArrayTrait::new()).unwrap();
    let returned_version = call(contract_address, 'get_transaction_version', @ArrayTrait::new()).unwrap();
    assert(*returned_version.at(0_u32) == 11, *returned_version.at(0_u32));

    let returned_contract_address = call(contract_address, 'get_account_contract_address', @ArrayTrait::new()).unwrap();
    assert(*returned_contract_address.at(0_u32) == 22, *returned_contract_address.at(0_u32));

    let returned_max_fee = call(contract_address, 'get_max_fee', @ArrayTrait::new()).unwrap();
    assert(*returned_max_fee.at(0_u32) == 33, *returned_max_fee.at(0_u32));

    let returned_chain_id = call(contract_address, 'get_chain_id', @ArrayTrait::new()).unwrap();
    assert(*returned_chain_id.at(0_u32) == 44, *returned_chain_id.at(0_u32));

    let returned_nonce = call(contract_address, 'get_nonce', @ArrayTrait::new()).unwrap();
    assert(*returned_nonce.at(0_u32) == 55, *returned_nonce.at(0_u32));

    let returned_signature = call(contract_address, 'get_signature', @ArrayTrait::new()).unwrap();
    assert(*returned_signature.at(1_u32) == 77, *returned_signature.at(1_u32));
    assert(*returned_signature.at(2_u32) == 88, *returned_signature.at(2_u32));
}

#[test]
fn test_spoof_max_fee() {
    let contract_address = deploy_contract('simple', @ArrayTrait::new()).unwrap();

    let mut tx_info = TxInfoMockTrait::default();
    tx_info.max_fee = Option::Some(33_u128);

    start_spoof(contract_address, tx_info);

    let returned_max_fee = call(contract_address, 'get_max_fee', @ArrayTrait::new()).unwrap();
    assert(*returned_max_fee.at(0_u32) == 33, *returned_max_fee.at(0_u32));
}

#[test]
fn test_start_stop_spoof_max_fee() {
    let contract_address = deploy_contract('simple', @ArrayTrait::new()).unwrap();
    let max_fee_before_mock = call(contract_address, 'get_max_fee', @ArrayTrait::new()).unwrap();

    let mut tx_info = TxInfoMockTrait::default();
    tx_info.max_fee = Option::Some(33_u128);

    start_spoof(contract_address, tx_info);

    let returned_max_fee = call(contract_address, 'get_max_fee', @ArrayTrait::new()).unwrap();
    assert(*returned_max_fee.at(0_u32) == 33, *returned_max_fee.at(0_u32));

    stop_spoof(contract_address);

    let returned_max_fee = call(contract_address, 'get_max_fee', @ArrayTrait::new()).unwrap();
    assert(*returned_max_fee.at(0_u32) == *max_fee_before_mock.at(0_u32), *returned_max_fee.at(0_u32));
}
