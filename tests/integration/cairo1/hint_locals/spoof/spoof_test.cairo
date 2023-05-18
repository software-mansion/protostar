use array::ArrayTrait;
use result::ResultTrait;
use cheatcodes::TxInfoMockTrait;

#[test]
fn test_spoof() {
    let contract_address = deploy_contract('simple', @ArrayTrait::new()).unwrap();

    let mut tx_info = TxInfoMockTrait::default();
    tx_info.transaction_hash = Option::Some(1234);
    start_spoof(contract_address, tx_info);
    // start_warp(100, contract_address).unwrap();

    invoke(contract_address, 'store_tx_hash', @ArrayTrait::new()).unwrap();
    let return_data = call(contract_address, 'get_stored_tx_hash', @ArrayTrait::new()).unwrap();
    assert(*return_data.at(0_u32) == 123, *return_data.at(0_u32));
}