# `declare`

```cairo
fn declare(contract: felt) -> Result::<felt, felt> nopanic;
```

Declares a contract given a contract name defined in the [protostar.toml](../../04-configuration-file.md) configuration
file.

- `contract` name of the contract as cairo shortstring (e.g. `declare('mycontract')`).