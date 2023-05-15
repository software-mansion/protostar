# Mocking TxInfo

## Context

Some use-cases like testing account contracts may require mocking the contents of `TxInfo` struct returned
by `get_tx_info()` syscall.

As of writing of this document, `TxInfo` is defined as follows

```cairo
struct TxInfo {
    // The version of the transaction. It is fixed (currently, 1) in the OS, and should be
    // signed by the account contract.
    // This field allows invalidating old transactions, whenever the meaning of the other
    // transaction fields is changed (in the OS).
    version: felt252,
    // The account contract from which this transaction originates.
    account_contract_address: ContractAddress,
    // The max_fee field of the transaction.
    max_fee: u128,
    // The signature of the transaction.
    signature: Span<felt252>,
    // The hash of the transaction.
    transaction_hash: felt252,
    // The identifier of the chain.
    // This field can be used to prevent replay of testnet transactions on mainnet.
    chain_id: felt252,
    // The transaction's nonce.
    nonce: felt252,
}
```

## Goal

Propose a solution for mocking contexts of `TxInfo`.

## Proposed solution

Introduce a new cheatcode `start_mock_tx_info` (working title) with a following signature

```cairo
fn start_mock_tx_info(contract_address: felt252, tx_info: TxInfoMock) -> Result::<(), felt252> nopanic

struct TxInfoMock {
    version: Option<felt252>,
    account_contract_address: Option<felt252>,
    max_fee: Option<u128>,
    signature: Option<Array<felt252>>,
    transaction_hash: Option<felt252>,
    chain_id: Option<felt252>,
    nonce: Option<felt252>,
}
```

and corresponding `stop_mock_tx_info` cheatcode, that will allow mocking all transactions and calls to the contract
given by `contract_address`.

`TxInfoMock` accepts `Option`s instead of plain values to allow mocking only parts of `get_tx_info()` response. For
fields with `None` provided, default values will be used instead of mocking.

Consecutive calls to `start_mock_tx_info` will modify the values of fields where `Some` was cancel (reset to default
value) mocks for fields where `None` was provided.

Additionally, `TxInfoMockTrait` and its implementation will be defined

```cairo
trait TxInfoMockTrait {
    fn default() -> TxInfoMock;
}

impl TxInfoMockImpl of TxInfoMockTrait {
    fn default() -> TxInfoMock {
        TxInfoMock {
            version: Option::None,
            account_contract_address: Option::None,
            max_fee: Option::None,
            signature: Option::None,
            transaction_hash: Option::None,
            chain_id: Option::None,
            nonce: Option::None,
        }
    }
}
```

This will allow the user to create an instance of `TxInfoMock` with default values and only modify necessary ones.

## Example usage

```cairo
#[test]
fn my_test() {
    // ...
    
    let mut tx_info = TxInfoMock::default();
    tx_info.signature = Option::Some(my_signature);
    tx_info.transaction_hash = Option::Some(1234);
    start_mock_tx_info(contract_address, tx_info).unwrap();
    
    // signature == my_signature
    // transaction_hash == 1234
    
    tx_info.transaction_hash = Option::Some(1111);
    start_mock_tx_info(contract_address, tx_info).unwrap();

    // signature == my_signature (Note no value changed)
    // transaction_hash == 1111
    
    tx_info.transaction_hash = Option::None;
    start_mock_tx_info(contract_address, tx_info).unwrap();

    // signature == my_signature (Note no value changed)
    // transaction_hash == default (Mock cancelled by passing Option::None)
    
    stop_mock_tx_info(contract_address).uwrap();
    
    // signature == default
    // transaction_hsah == default
}
```
