# `declare`

```cairo
fn declare(contract: felt252) -> Result::<felt252, felt252> nopanic;
```

Declares a contract given its name defined in the [protostar.toml](../../05-protostar-toml.md) configuration
file.

- `contract` name of a contract as cairo shortstring (e.g. `declare('mycontract')`).

:::info
Declare only supports Cairo1 (new syntax) contracts. To declare old cairo0 contracts,
use [declare_cairo0](./declare-cairo0.md).
:::

```cairo title="Example"
use result::ResultTrait;

#[test]
fn test_declare() {
    let class_hash = declare('mycontract').unwrap();
    // ...
}
```