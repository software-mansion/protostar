# `prepare`

```cairo
fn prepare(class_hash: felt252, calldata: @Array::<felt252>) -> Result::<PreparedContract, felt252> nopanic;
```

Prepares contract for deployment.

```cairo title="Example"
use result::ResultTrait;
use array::ArrayTrait;

fn my_function() {
    let class_hash = declare('mycontract').unwrap();

    let mut calldata = ArrayTrait::new();
    calldata.append(10);
    calldata.append(11);
    calldata.append(12);

    let prepared_contract = prepare(class_hash, @calldata).unwrap();

    // ...
}
```