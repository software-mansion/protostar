# `deploy_contract`

```cairo
fn deploy_contract(contract: felt252, calldata: Array::<felt252>) -> 
Result::<felt252, RevertedTransaction>
```

Declares and deploys a contract given its name defined in the [protostar.toml](../../04-protostar-toml.md) configuration
file.

```cairo title="Example"
use result::ResultTrait;
use array::ArrayTrait;

fn my_function() {

    let mut calldata = ArrayTrait::new();
    calldata.append(10);
    calldata.append(11);
    calldata.append(12);

    let address = deploy_contract('mycontract', calldata).unwrap();

    // ...
}
```

Errors raised by the constructor can be handled in the same way as for [deploy](./deploy.md)


:::info
`deploy_contract` is just a function which calls cheatcodes `declare` -> `prepare` -> `deploy`,  and it's what it does under the hood.
:::
