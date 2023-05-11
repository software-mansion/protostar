# `invoke`

```cairo
fn invoke(contract_address: felt252, function_name: felt252, calldata: Array::<felt252>) -> Result::<(), RevertedTransaction> nopanic;

struct RevertedTransaction {
    panic_data: Array::<felt252>, 
}

trait RevertedTransactionTrait {
    fn first(self: @RevertedTransaction) -> felt252;
}
```

Invokes a contract's function. `function_name` parameter should be provided as a short string. `invoke` can mutate the state of the contract and does not return a value, to query the contract for values use [call](./call.md). 

```cairo title="Example"
use result::ResultTrait;
use array::ArrayTrait;

#[test]
fn invoke_test() {

    let contract_address = 123;

    let mut calldata = ArrayTrait::new();
    calldata.append(10);
    calldata.append(11);
    calldata.append(12);

    invoke(contract_address, 'function_name', calldata).unwrap();

    // ...
}
```

## Handling invoke failures
```cairo title="Deployed contract"
#[contract]
mod MinimalContract {
    #[external]
    fn panic_with(panic_data: Array::<felt252>) {
        panic(panic_data);
    }
}
```

```cairo title="Test"
use cheatcodes::RevertedTransactionTrait;

#[test]
fn test_invoke_errors() {
    let mut panic_data = ArrayTrait::new();
    panic_data.append(2); // Array length
    panic_data.append('error');
    panic_data.append('data');
    
    match invoke(deployed_contract_address, 'panic_with', panic_data) {
        Result::Ok(x) => assert(false, 'Shouldnt have succeeded'),
        Result::Err(x) => {
            assert(x.first() == 'error', 'first datum doesnt match');
            assert(*x.panic_data.at(1_u32) == 'data', 'second datum doesnt match');
        }
    }
}
```
