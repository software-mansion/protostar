---
sidebar_label: Integration testing
---

# Integration testing

Using [unit testing](./01-unit-testing.md) as much as possible is a good practice, as it makes your test suites run faster. However, when writing smart contracts you often want your test to cover the on-chain state and interactions between multiple contracts.

In this section, you will learn how to deploy and interact with a smart contract in Protostar for testing purposes. 

## How to test a contract
To test a contract you need to use an important Protostar feature:  [cheatcodes](./03-cheatcodes.md). Cheatcodes are additional library functions that Protostar exposes to help you with testing.

Let's write a test which deploys and calls a contract. First let's define our contract 

```cairo title="Deployed contract"
#[contract]
mod MinimalContract {
    #[external]
    fn hello() {
        // ...
    }
}
```

We can write a test that deploys and calls this contract. Let's create a file `test_contract.cairo`:
```cairo title="Example"
use array::ArrayTrait;
use result::ResultTrait;

#[test]
fn test_deploy() {
    let deployed_contract_address = deploy_contract('minimal', ArrayTrait::new()).unwrap();
    invoke(deployed_contract_address, 'hello', ArrayTrait::new()).unwrap();
}
```
This cheatcode will declare and deploy the given contract.

## Transaction reverts

Cheatcodes [deploy](./cheatcodes-reference/deploy.md), [invoke](./cheatcodes-reference/invoke.md) and [call](./cheatcodes-reference/call.md) execute code on chain which can be reverted.
In such case, they return `RevertedTransaction` structure. You can use it, for example, to verify if your contract reverts the transaction in a certain scenario.

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
use array::ArrayTrait;

#[test]
fn test_invoke_errors() {
    let deployed_contract_address = deploy_contract('minimal_contract', ArrayTrait::new());
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
```

## Under the hood
You may ask, where the contract has been deployed? Protostar comes with a local Starknet instance which you can use to test your contracts. 
To encourage good testing practices, each test case starts with a fresh Starknet instance. 

When Starknet instance is accessed through cheatcodes, it is analogous to accessing real Starknet through gateway. An example consequence of this behavior is that `get_caller_address` will return `0` in the called contract.

## Old cairo contracts

Protostar allows you to test contracts written in old cairo. You can use cheatcode [declare_cairo0](./cheatcodes-reference/declare-cairo0.md) to declare them.