---
sidebar_label: Integration testing
---

# Integration testing (TODO)

Using [unit testing](./01-unit-testing.md) as much as possible is a good practice, as it makes your test suites faster. However, when writing smart contracts you often want your test to cover on-chain state and interactions between multiple contracts.

## How to test a contract

Protostar comes with a local Starknet instance which you can use to test your contracts. To access it you need to use [cheatcodes](./cheatcodes-refernce/). 

Let's write a test which deploys and calls a contract. First let's define our contract 

```cairo title="Deployed contract"
#[contract]
mod MinimalContract {
    #[external]
    fn panic_with(panic_data: Array::<felt252>) {
        panic(panic_data);
    }
}
```

We can write a test which deploys and calls this contract. Let's create a file `test_contract.cairo`:
```cairo title="Example"
use array::ArrayTrait;
use result::ResultTrait;

#[test]
fn test_deploy() {
    let class_hash = declare('minimal').unwrap();
    assert(class_hash != 0, 'class_hash != 0');

    let prepare_result = prepare(class_hash, ArrayTrait::new()).unwrap();

    assert(prepare_result.contract_address != 0, 'prepared contract_address != 0');
    assert(prepare_result.class_hash != 0, 'prepared class_hash != 0');

    let prepared_contract = PreparedContract {
        contract_address: prepare_result.contract_address,
        class_hash: prepare_result.class_hash,
        constructor_calldata: prepare_result.constructor_calldata
    };
    let deployed_contract_address = deploy(prepared_contract).unwrap();
    assert(deployed_contract_address != 0, 'deployed_contract_address != 0');
}
```


## Complex arguments
TODO (examples with complex data types)

## Transaction reverts

[deploy](./cheatcodes-refernce/deploy.md), [invoke](./cheatcodes-refernce/invoke.md) and [call](./cheatcodes-refernce/call.md) execute code on chain which can be reverted.
In such case, they return `RevertedTransaction` structure. You can use it, for example, to verify if transaction reverts with a specific error message.

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

