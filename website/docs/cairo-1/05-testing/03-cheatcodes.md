---
sidebar_label: Cheatcodes
---

# Cheatcodes

Often while testing your contract you want to emulate complex scenarios. As an example, you might want to test how your contract behaves when not-authorized contract calls it. Protostar let's you tests such scenarios with *cheatcodes*. In this section you will learn what cheatcodes are and how to use them to create strong tests for your contracts.


## Let's prank a contract

Assume you want to test a user validation mechanism in your contract. You can leverage [start_prank](./cheatcodes-reference/start_prank.md) cheatcode to do that. Let's write a simple contract which validates caller address.

```cairo title="Deployed contract"
#[contract]
mod MinimalContract {
    #[external]
    fn is_expected_user() {
        let caller_address = get_caller_address();
        assert(caller_address == 123, 'not authorized');
    }
}
```

We know [from previous section](./02-integration-testing.md#under-the-hood) that if we call `is_expected_user` method, `caller_address` will be `0`. To pass such test we have to use [start_prank](./cheatcodes-reference/start_prank.md) cheatcode. It sets the value returned by `get_caller_address()` for a targeted contract.

```cairo title="Test"
use cheatcodes::RevertedTransactionTrait;

#[test]
fn test_invoke_errors() {
    let contract_address = deploy('minimal_contract', ArrayTrait::new());
    start_prank(contract_address, 123);
    invoke(contract_address, 'is_expected_user', ArrayTrait::new()).unwrap();
```

Such test will pass.

## Other cheatcodes

You can find a list of all available cheatcodes in [cheatcode reference](./cheatcodes-reference/README.md)
