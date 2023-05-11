---
sidebar_label: Cheatcodes
---

# Cheatcodes

Often while testing your contract you want to emulate complex scenarios. As an example, you might want to test how your contract behaves when not-authorized contract calls it. Protostar let's you tests such scenarios with *cheatcodes*. In this section you will learn what cheatcodes are and how to use them to create strong tests for your contracts.


## Let's prank a contract

Assume you want to test a user validation mechanism in your contract. You can leverage [start_prank](./cheatcodes-refernce/start_prank.md) cheatcode to do that.

TODO correct code example
```cairo title="Deployed contract"
#[contract]
mod MinimalContract {
    #[external]
    fn is_expected_user() {
        (TODO add validating code)
    }
}
```
```cairo title="Test"
use cheatcodes::RevertedTransactionTrait;

#[test]
fn test_invoke_errors() {
    let mut contract_address = ArrayTrait::new();
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

## What about the constructors?

What in case you want to prank the constructor code? You can prank your contract before it's deployed! To do that 

TODO add example

## Other cheatcodes

You can find a list of all available cheatcodes in [cheatcode reference](./cheatcodes-refernce/README.md)
