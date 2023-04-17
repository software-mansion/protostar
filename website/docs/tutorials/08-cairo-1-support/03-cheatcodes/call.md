# `call`

```cairo
extern fn call(contract: felt252, function_name: felt252, calldata: Array::<felt252>) -> Result::<(Array::<felt252>), felt252> nopanic;
```

Calls a [deployed](./deploy.md) contract. Unlike [invoke](./invoke.md), it **does not** mutate the blockchain state.

- `contract` - deployed contract address
- `function_name` - the name of the function you wish to call, this is the [Cairo short string](https://www.cairo-lang.org/docs/how_cairo_works/consts.html#short-string-literals) which can be at most 31-characters long.
- `calldata` - arguments to the target function

```cairo title="Example"
use array::ArrayTrait;
use result::ResultTrait;

#[test]
fn test_call_simple() {
    let class_hash = declare('simple').unwrap();
    assert(class_hash != 0, 'class_hash != 0');

    let prepare_result = prepare(class_hash, ArrayTrait::new()).unwrap();

    assert(prepare_result.contract_address != 0, 'deployed contract_address != 0');
    assert(prepare_result.class_hash != 0, 'deployed class_hash != 0');

    let prepared_contract = PreparedContract {
        contract_address: prepare_result.contract_address,
        class_hash: prepare_result.class_hash,
        constructor_calldata: prepare_result.constructor_calldata
    };
    let deployed_contract_address = deploy(prepared_contract).unwrap();
    assert(deployed_contract_address != 0, 'deployed_contract_address != 0');

    let return_data = call(deployed_contract_address, 'empty', ArrayTrait::new()).unwrap();
    assert(return_data.is_empty(), 'call result is empty');

    let mut calldata = ArrayTrait::new();
    calldata.append(3);
    calldata.append(2);
    calldata.append(5);
    let return_data2 = call(deployed_contract_address, 'perform', calldata).unwrap();
    assert(*return_data2.at(0_u32) == 25, 'check call result');
}
```

You can find more examples [here](https://github.com/software-mansion/protostar/blob/18959214d46409be8bedd92cc6427c1945b1bcc8/tests/integration/cairo1_hint_locals/call/call_test.cairo).
