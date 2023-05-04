# `invoke`

```cairo
fn invoke(contract_address: felt252, function_name: felt252, calldata: @Array::<felt252>) -> Result::<(), RevertedTransaction> nopanic;

struct RevertedTransaction {
    panic_data: Array::<felt252>, 
}

trait RevertedTransactionTrait {
    fn first(self: @RevertedTransaction) -> felt252;
}
```

Invokes a contract's function. `function_name` parameter should be provided as a short string. `invoke` can mutate the
state of the contract and does not return a value, to query the contract for values use [call](./call.md).

```cairo title="Example"
use result::ResultTrait;
use array::ArrayTrait;

#[test]
fn test_invoke() {

    let contract_address = 123;

    let mut calldata = ArrayTrait::new();
    calldata.append(10);
    calldata.append(11);
    calldata.append(12);

    invoke(contract_address, 'function_name', @calldata).unwrap();

    // ...
}
```
