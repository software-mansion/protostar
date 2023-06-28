# `start_spoof`

```cairo
fn start_spoof(contract_address: felt252, mock: TxInfoMock) nopanic;
```

Changes `TxInfo` returned by `get_tx_info()` for the targeted contract until the spoof is stopped
with [stop_spoof](./stop_spoof.md).

- `contract_address` address of the contract for which `get_tx_info()` result will be mocked.
- `TxInfoMock` - a struct with same structure as `TxInfo` (returned by `get_tx_info()`), fields are optional to allow
  partial mocking of the `TxInfo`, i.e. for those fields that are `Option::None`, `get_tx_info` will return original
  values.

```cairo title="TxInfoMock"
struct TxInfoMock {
    version: Option<felt252>,
    account_contract_address: Option<felt252>,
    max_fee: Option<u128>,
    signature: Option<Array<felt252>>,
    transaction_hash: Option<felt252>,
    chain_id: Option<felt252>,
    nonce: Option<felt252>,
}

trait TxInfoMockTrait {
    // Returns a default object initialized with Option::None for each field  
    fn default() -> TxInfoMock;
}
```

```cairo title="Contract example"
#[contract]
mod SimpleContract {
    use box::BoxTrait;
    use starknet::info::get_tx_info;

    struct Storage {
        stored_hash: felt252
    }

    #[external]
    fn store_tx_hash() {
        let tx_info = get_tx_info().unbox();
        stored_hash::write(tx_info.transaction_hash);
    }

    #[view]
    fn get_stored_tx_hash() -> felt252 {
        stored_hash::read()
    }
}
```

```cairo title="Test example"
use array::ArrayTrait;
use result::ResultTrait;
use cheatcodes::TxInfoMockTrait;
use option::OptionTrait;


#[test]
fn test_start_spoof() {
    let contract_address = deploy_contract('simple', @ArrayTrait::new()).unwrap();
    let version_before_mock = call(contract_address, 'get_transaction_version', @ArrayTrait::new()).unwrap();

    // Set tx_hash to 1234
    let mut tx_info = TxInfoMockTrait::default();
    tx_info.transaction_hash = Option::Some(1234);
    start_spoof(contract_address, tx_info);

    // Stores tx_hash in contract storage
    invoke(contract_address, 'store_tx_hash', @ArrayTrait::new()).unwrap();
    // Retrieve stored tx_hash
    let return_data = call(contract_address, 'get_stored_tx_hash', @ArrayTrait::new()).unwrap();
    assert(*return_data.at(0_u32) == 1234, *return_data.at(0_u32));

    // Verify that none of the other fields have been mocked
    let return_data = call(contract_address, 'get_transaction_version', @ArrayTrait::new()).unwrap();
    assert(*return_data.at(0_u32) == *version_before_mock.at(0_u32), *return_data.at(0_u32));
}
```