# `declare_cairo0`

```cairo
fn declare_cairo0(contract: felt252) -> Result::<felt252, felt252> nopanic;
```
Declares a Cairo0 (old syntax) contract given a contract name defined in the [protostar.toml](../../05-protostar-toml.md) configuration file.

- `contract` name of a contract as Cairo shortstring (e.g. `declare_cairo0('mycontract')`).

```cairo title="Example"
use result::ResultTrait;

#[test]
fn test_declare_cairo0() {
    let class_hash = declare_cairo0('myoldcontract').unwrap();
    // ...
}
```