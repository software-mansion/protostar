use array::ArrayTrait;
use result::ResultTrait;
use cheatcodes::TxInfoMockTrait;
use option::OptionTrait;


#[test]
fn test_start_spoof_transaction_hash_doesnt_affect_other_fields() {
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

fn assert_all_except_signature(
    contract_address: felt252,
    expected_max_fee: felt252,
    expected_version: felt252,
    expected_tx_hash: felt252,
    expected_chain_id: felt252,
    expected_nonce: felt252,
    expected_account_contract_address: felt252
) {
    invoke(contract_address, 'store_tx_hash', @ArrayTrait::new()).unwrap();
    let return_data = call(contract_address, 'get_stored_tx_hash', @ArrayTrait::new()).unwrap();
    assert(*return_data.at(0_u32) == expected_tx_hash, *return_data.at(0_u32));

    let returned_version = call(contract_address, 'get_transaction_version', @ArrayTrait::new()).unwrap();
    assert(*returned_version.at(0_u32) == expected_version, *returned_version.at(0_u32));

    let returned_contract_address = call(contract_address, 'get_account_contract_address', @ArrayTrait::new()).unwrap();
    assert(*returned_contract_address.at(0_u32) == expected_account_contract_address, *returned_contract_address.at(0_u32));

    let returned_max_fee = call(contract_address, 'get_max_fee', @ArrayTrait::new()).unwrap();
    assert(*returned_max_fee.at(0_u32) == expected_max_fee, *returned_max_fee.at(0_u32));

    let returned_chain_id = call(contract_address, 'get_chain_id', @ArrayTrait::new()).unwrap();
    assert(*returned_chain_id.at(0_u32) == expected_chain_id, *returned_chain_id.at(0_u32));

    let returned_nonce = call(contract_address, 'get_nonce', @ArrayTrait::new()).unwrap();
    assert(*returned_nonce.at(0_u32) == expected_nonce, *returned_nonce.at(0_u32));
}

#[test]
fn test_spoof_tx_info() {
    let contract_address = deploy_contract('simple', @ArrayTrait::new()).unwrap();

    let max_fee_before_mock = call(contract_address, 'get_max_fee', @ArrayTrait::new()).unwrap();
    let transaction_version_before_mock = call(contract_address, 'get_transaction_version', @ArrayTrait::new()).unwrap();
    let tx_hash_before_mock = call(contract_address, 'get_stored_tx_hash', @ArrayTrait::new()).unwrap();
    let chain_id_before_mock = call(contract_address, 'get_chain_id', @ArrayTrait::new()).unwrap();
    let signature_before_mock = call(contract_address, 'get_signature', @ArrayTrait::new()).unwrap();
    let nonce_before_mock = call(contract_address, 'get_nonce', @ArrayTrait::new()).unwrap();
    let account_contract_address_before_mock = call(contract_address, 'get_account_contract_address', @ArrayTrait::new()).unwrap();

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

    assert_all_except_signature(
        contract_address: contract_address,
        expected_max_fee: 33,
        expected_version: 11,
        expected_tx_hash: 66,
        expected_chain_id: 44,
        expected_nonce: 55,
        expected_account_contract_address: 22
    );
    let returned_signature = call(contract_address, 'get_signature', @ArrayTrait::new()).unwrap();
    assert(*returned_signature.at(0_u32) == 2, *returned_signature.at(0_u32));
    assert(*returned_signature.at(1_u32) == 77, *returned_signature.at(1_u32));
    assert(*returned_signature.at(2_u32) == 88, *returned_signature.at(2_u32));


    stop_spoof(contract_address);

    assert_all_except_signature(
        contract_address: contract_address,
        expected_max_fee: *max_fee_before_mock.at(0_u32),
        expected_version: *transaction_version_before_mock.at(0_u32),
        expected_tx_hash: *tx_hash_before_mock.at(0_u32),
        expected_chain_id: *chain_id_before_mock.at(0_u32),
        expected_nonce: *nonce_before_mock.at(0_u32),
        expected_account_contract_address: *account_contract_address_before_mock.at(0_u32)
    );
    let returned_signature = call(contract_address, 'get_signature', @ArrayTrait::new()).unwrap();
    assert(*returned_signature.at(0_u32) == *signature_before_mock.at(0_u32), *returned_signature.at(0_u32));
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

#[test]
fn test_stop_spoof_on_non_existent() {
    stop_spoof(1234);
    assert(1==1, 1); //needed because stop_spoof not panicable
}

#[test]
fn test_stop_spoof_on_not_spoofed() {
    let contract_address = deploy_contract('simple', @ArrayTrait::new()).unwrap();
    let max_fee_before = call(contract_address, 'get_max_fee', @ArrayTrait::new()).unwrap();

    stop_spoof(contract_address);

    let returned_max_fee = call(contract_address, 'get_max_fee', @ArrayTrait::new()).unwrap();
    assert(*returned_max_fee.at(0_u32) == *max_fee_before.at(0_u32), *returned_max_fee.at(0_u32));
}

#[test]
fn test_stop_spoof_multiple_times() {
    let contract_address = deploy_contract('simple', @ArrayTrait::new()).unwrap();
    let max_fee_before_mock = call(contract_address, 'get_max_fee', @ArrayTrait::new()).unwrap();

    let mut tx_info = TxInfoMockTrait::default();
    tx_info.max_fee = Option::Some(33_u128);

    start_spoof(contract_address, tx_info);

    let returned_max_fee = call(contract_address, 'get_max_fee', @ArrayTrait::new()).unwrap();
    assert(*returned_max_fee.at(0_u32) == 33, *returned_max_fee.at(0_u32));

    stop_spoof(contract_address);
    stop_spoof(contract_address);

    let returned_max_fee = call(contract_address, 'get_max_fee', @ArrayTrait::new()).unwrap();
    assert(*returned_max_fee.at(0_u32) == *max_fee_before_mock.at(0_u32), *returned_max_fee.at(0_u32));
}

#[test]
fn test_stop_spoof_cancels_all_spoofs() {
    let contract_address = deploy_contract('simple', @ArrayTrait::new()).unwrap();
    let max_fee_before_mock = call(contract_address, 'get_max_fee', @ArrayTrait::new()).unwrap();

    let mut tx_info1 = TxInfoMockTrait::default();
    tx_info1.max_fee = Option::Some(33_u128);
    start_spoof(contract_address, tx_info1);

    let mut tx_info2 = TxInfoMockTrait::default();
    tx_info2.max_fee = Option::Some(44_u128);
    start_spoof(contract_address, tx_info2);

    let returned_max_fee = call(contract_address, 'get_max_fee', @ArrayTrait::new()).unwrap();
    assert(*returned_max_fee.at(0_u32) == 44, *returned_max_fee.at(0_u32));

    stop_spoof(contract_address);

    let returned_max_fee = call(contract_address, 'get_max_fee', @ArrayTrait::new()).unwrap();
    assert(*returned_max_fee.at(0_u32) == *max_fee_before_mock.at(0_u32), *returned_max_fee.at(0_u32));
}

#[test]
fn test_start_spoof_latest_takes_precedence() {
    let contract_address = deploy_contract('simple', @ArrayTrait::new()).unwrap();

    let mut tx_info1 = TxInfoMockTrait::default();
    tx_info1.max_fee = Option::Some(22_u128);
    start_spoof(contract_address, tx_info1);

    let mut tx_info2 = TxInfoMockTrait::default();
    tx_info2.max_fee = Option::Some(33_u128);
    start_spoof(contract_address, tx_info2);

    let returned_max_fee = call(contract_address, 'get_max_fee', @ArrayTrait::new()).unwrap();
    assert(*returned_max_fee.at(0_u32) == 33, *returned_max_fee.at(0_u32));

    let mut tx_info1 = TxInfoMockTrait::default();
    tx_info1.max_fee = Option::Some(33_u128);
    start_spoof(contract_address, tx_info1);

    let mut tx_info2 = TxInfoMockTrait::default();
    tx_info2.max_fee = Option::Some(22_u128);
    start_spoof(contract_address, tx_info2);

    let returned_max_fee = call(contract_address, 'get_max_fee', @ArrayTrait::new()).unwrap();
    assert(*returned_max_fee.at(0_u32) == 22, *returned_max_fee.at(0_u32));
}

#[test]
fn test_spoof_multiple_times() {
    let contract_address = deploy_contract('simple', @ArrayTrait::new()).unwrap();
    let max_fee_before_mock = call(contract_address, 'get_max_fee', @ArrayTrait::new()).unwrap();

    let mut tx_info = TxInfoMockTrait::default();
    tx_info.max_fee = Option::Some(33_u128);

    start_spoof(contract_address, tx_info);

    let returned_max_fee = call(contract_address, 'get_max_fee', @ArrayTrait::new()).unwrap();
    assert(*returned_max_fee.at(0_u32) == 33, *returned_max_fee.at(0_u32));

    stop_spoof(contract_address);

    // repeat
    let mut tx_info = TxInfoMockTrait::default();
    tx_info.max_fee = Option::Some(33_u128);

    start_spoof(contract_address, tx_info);

    let returned_max_fee = call(contract_address, 'get_max_fee', @ArrayTrait::new()).unwrap();
    assert(*returned_max_fee.at(0_u32) == 33, *returned_max_fee.at(0_u32));

    stop_spoof(contract_address);

    let returned_max_fee = call(contract_address, 'get_max_fee', @ArrayTrait::new()).unwrap();
    assert(*returned_max_fee.at(0_u32) == *max_fee_before_mock.at(0_u32), *returned_max_fee.at(0_u32));
}
