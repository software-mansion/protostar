# `deploy_contract_cairo0`

```cairo
fn deploy_contract_cairo0(contract: felt252, calldata: @Array::<felt252>) -> 
Result::<felt252, RevertedTransaction>
```

Declares and deploys a Cairo 0 contract given its name defined in the [protostar.toml](../../05-protostar-toml.md)
configuration file.

```cairo title="Example"
use result::ResultTrait;
use array::ArrayTrait;

#[test]
fn test_deploy_contract_cairo0() {
    let mut calldata = ArrayTrait::new();
    calldata.append(10);
    calldata.append(11);
    calldata.append(12);

    let address = deploy_contract_cairo0('mycontract', @calldata).unwrap();

    // ...
}
```

:::info
`deploy_contract_cairo0` is just a function which calls cheatcodes `declare_cairo0` -> `prepare` -> `deploy`, and it's
what it does under the hood.
:::

