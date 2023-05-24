---
sidebar_label: Integration testing
---

# Integration testing

Using [unit testing](./01-unit-testing.md) as much as possible is a good practice, as it makes your test suites run faster. However, when writing smart contracts you often want your test to cover the on-chain state and interactions between multiple contracts.

In this section, you will learn how to deploy and interact with a smart contract in Protostar for testing purposes. 

## How to test a contract
To test a contract you need to use an important Protostar feature:  [cheatcodes](./03-cheatcodes.md). Cheatcodes are additional library functions that Protostar exposes to help you with testing.

Let's write a test which deploys and calls a contract. First let's define our contract in the file `src/lib.cairo`

```cairo title="Deployed contract"
#[contract]
mod MinimalContract {
    #[external]
    fn hello() {
        assert(5 == 5, 'always true');
    }
}
```

You need to define contract in [protostar.toml](../04-protostar-toml.md) configuration
file. Add it to the `[contracts]` section
```toml title="Configuration file"
[contracts]
minimal = ["your_project_name"]
```

We can write a test that deploys and calls this contract. Let's create a file `test_contract.cairo`:
```cairo title="Example"
use array::ArrayTrait;
use result::ResultTrait;

#[test]
fn test_deploy() {
    let deployed_contract_address = deploy_contract('minimal', @ArrayTrait::new()).unwrap();
    invoke(deployed_contract_address, 'hello', @ArrayTrait::new()).unwrap();
}
```
[deploy_contract](./cheatcodes-reference/deploy_contract.md) will declare and deploy the given contract. [invoke](./cheatcodes-reference/invoke.md) will invoke `hello` method.

## Transaction reverts

Cheatcodes [deploy](./cheatcodes-reference/deploy.md), [invoke](./cheatcodes-reference/invoke.md) and [call](./cheatcodes-reference/call.md) execute code on chain which can be reverted.
In such case, they return `RevertedTransaction` structure. You can use it, for example, to verify if your contract reverts the transaction in a certain scenario.

Here's how the structure looks: 

```#[derive(Drop, Clone)]
struct RevertedTransaction {
    panic_data: Array::<felt252>, 
}

trait RevertedTransactionTrait {
    fn first(self: @RevertedTransaction) -> felt252; // Gets the first felt of the panic data
}
```

### Example usage

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
use result::ResultTrait;

#[test]
fn test_invoke_errors() {
    let deployed_contract_address = deploy_contract('minimal', @ArrayTrait::new()).unwrap();
    let mut panic_data = ArrayTrait::new();
    panic_data.append(2); // Array length
    panic_data.append('error');
    panic_data.append('data');
    
    match invoke(deployed_contract_address, 'panic_with', @panic_data) {
        Result::Ok(x) => assert(false, 'Shouldnt have succeeded'),
        Result::Err(x) => {
            assert(x.first() == 'error', 'first datum doesnt match');
            assert(*x.panic_data.at(1_u32) == 'data', 'second datum doesnt match');
        }
    }
}
```

## Cheatcodes in contract constructors

If you ever want to use `prank`, `roll`, `warp` or any of the environment-modifying cheatcodes in the constructor code, just 
split the `deploy_contract` into `declare`, `prepare` and `deploy` - so that you have a contract address 
(from `prepare` call) just before the deployment. Then you can use the cheatcode of your choice on the obtained address,
and it will work in the constructor as well!


### Example:
```cairo title="with_constructor.cairo"
#[contract]
mod WithConstructor {
    use starknet::get_caller_address;
    use starknet::ContractAddress;
    use starknet::ContractAddressIntoFelt252;
    use traits::Into;


    struct Storage {
        owner: ContractAddress,
    }

    #[constructor]
    fn constructor() {
        let caller_address = get_caller_address();
        owner::write(caller_address);
    }

    #[view]
    fn get_owner() -> felt252 {
        owner::read().into()
    }
}

```

```cairo title="test_with_constructor.cairo"
#[test]
fn test_prank_constructor() {
    let class_hash = declare('with_constructor').unwrap();
    let prepared = prepare(class_hash, @ArrayTrait::new()).unwrap();
    let owner_address = 123;

    start_prank(owner_address, prepared.contract_address).unwrap(); // <-- Prank before the deploy call

    let deployed_contract_address = deploy(prepared).unwrap();

    let return_data = call(deployed_contract_address, 'get_owner', @ArrayTrait::new()).unwrap();
    assert(*return_data.at(0_u32) == owner_address, 'check call result');
}
```

## Under the hood
You may ask, where the contract has been deployed? Protostar comes with a local Starknet instance which you can use to test your contracts. 
To encourage good testing practices, each test case starts with a fresh Starknet instance. 

When Starknet instance is accessed through cheatcodes, it is analogous to accessing real Starknet through gateway. An example consequence of this behavior is that `get_caller_address` will return `0` in the called contract.

## Old cairo contracts

Protostar allows you to test contracts written in old cairo. You can use cheatcode [declare_cairo0](./cheatcodes-reference/declare-cairo0.md) to declare them.

## Working with complex argument types

Your `#[view]` , `#[external]` or `#[constructor]` might require complex argument types as inputs. 

Given a contract:


```cairo title="Tested contract"
#[contract]
mod ExampleContract {
    #[derive(Drop, Serde)]
    struct NestedStruct {
        d: felt252,
    }

    #[derive(Drop, Serde)]
    struct CustomStruct {
        a: felt252,
        b: felt252,
        c: NestedStruct,
    }

    #[derive(Drop, Serde)]
    struct AnotherCustomStruct {
        e: felt252,
    }

    #[view]
    fn add_multiple_parts(custom_struct: CustomStruct, another_struct: AnotherCustomStruct, standalone_arg: felt252) -> felt252 {
        custom_struct.a + custom_struct.b + custom_struct.c.d + another_struct.e + standalone_arg
    }
```

You can test the `#[view]` using `Serde` to serialize the arguments into calldata (just like an external contract call would work)

```cairo title="ExampleContract test"
use array::ArrayTrait;
use result::ResultTrait;
use serde::Serde;

use example::contract::example::ExampleContract::CustomStruct;
use example::contract::example::ExampleContract::NestedStruct;
use example::contract::example::ExampleContract::AnotherCustomStruct;

#[test]
fn test_add_multiple_structs() {
    let contract_address = deploy_contract('example', @ArrayTrait::new()).unwrap();

    let mut calldata = ArrayTrait::new();

    let ns = NestedStruct { d: 1 };
    let cs = CustomStruct { a: 2, b: 3, c: ns };
    let acs = AnotherCustomStruct { e: 4 };
    let standalone_arg = 5;

    Serde::serialize(@cs, ref calldata);  // First argument
    Serde::serialize(@acs, ref calldata); // Second argument
    calldata.append(standalone_arg);      // Third argument (no need for serde call here) 

    let result = call(contract_address, 'add_multiple_parts', @calldata).unwrap();
    assert(*result.at(0_usize) == 1 + 2 + 3 + 4 + 5, 'Invalid sum');
}
```

You would use the same method for passing arguments for `deploy_contract`, `deploy` or `invoke` cheatcodes.
