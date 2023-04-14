# `invoke`

```cairo
fn invoke(contract_address: felt252, function_name: felt252, calldata: Array::<felt252>) -> Result::<(), felt252> nopanic;
```

Invokes a contract. `function_name` parameter should be provided as a shortstring.

```cairo title="Example"
use result::ResultTrait;
use array::ArrayTrait;

fn my_function() {

    let address = 123;

    let mut calldata = ArrayTrait::new();
    calldata.append(10);
    calldata.append(11);
    calldata.append(12);

    invoke(address, 'function_name', calldata).unwrap();

    // ...
}
```