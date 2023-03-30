# `declare`

```cairo
fn declare(contract: felt) -> Result::<felt, felt> nopanic;
```

Declares a contract given a contract name defined in the [protostar.toml](../../04-configuration-file.md) configuration
file.

:::info
Declare only supports Cairo1 (new syntax) contracts. To declare old cairo0 contracts,
use [declare_cairo0](./declare-cairo0.md).
:::

- `contract` name of the contract as cairo shortstring (e.g. `declare('mycontract')`).