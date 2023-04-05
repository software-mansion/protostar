# `declare`

```cairo
fn declare(contract: felt) -> Result::<felt, felt> nopanic;
```

Declares a contract given its name defined in the [protostar.toml](../../04-configuration-file.md) configuration
file.

- `contract` name of a contract as cairo shortstring (e.g. `declare('mycontract')`).

:::info
Declare only supports Cairo1 (new syntax) contracts. To declare old cairo0 contracts,
use [declare_cairo0](./declare-cairo0.md).
:::

```cairo title="Example"
use result::ResultTrait;

fn my_function() {
    let class_hash = declare('mycontract').unwrap();
    // ...
}
```