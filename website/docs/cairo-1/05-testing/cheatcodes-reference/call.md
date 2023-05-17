# `call`

```cairo
extern fn call(contract: felt252, function_name: felt252, calldata: @Array::<felt252>) -> Result::<(Array::<felt252>), RevertedTransaction> nopanic;

struct RevertedTransaction {
    panic_data: Array::<felt252>, 
}

trait RevertedTransactionTrait {
    fn first(self: @RevertedTransaction) -> felt252;
}
```

Calls a [deployed](./deploy.md) contract. Unlike [invoke](./invoke.md), it **does not** mutate the blockchain state.

- `contract` - deployed contract address
- `function_name` - the name of the function you wish to call, this is the [Cairo short string](https://www.cairo-lang.org/docs/how_cairo_works/consts.html#short-string-literals) which can be at most 31-characters long.
- `calldata` - arguments to the target function

```cairo title="Example"
use array::ArrayTrait;
use result::ResultTrait;

#[test]
fn test_call() {
    let mut calldata = ArrayTrait::new();
    calldata.append(3);
    calldata.append(2);
    calldata.append(5);
    let return_data2 = call(deployed_contract_address, 'foo', @calldata).unwrap();
    assert(*return_data2.at(0_u32) == 25, 'check call result');
}
```

You can find more examples [here](https://github.com/software-mansion/protostar/blob/18959214d46409be8bedd92cc6427c1945b1bcc8/tests/integration/cairo1_hint_locals/call/call_test.cairo).
