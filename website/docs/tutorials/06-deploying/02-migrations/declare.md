# `declare`

```python
def declare(
    contract_path_str: str,
    *,
    config: Optional[CheatcodeNetworkConfig] = None
) -> DeclaredContract:

class DeclaredContract:
    class_hash: int
```

Sends a declare transaction.

- `contract_path_str` — A path to the **compiled** contract or a [contract name](../../compiling#contract-name). If you provide a contract name, Protostar will compile the contract to the migration output directory.
- `config` — A keyword only argument that allows passing [network configuration](../03-network-config.md).

## Example

```cairo
%lang starknet

@external
func up() {
    %{ declare("main", config={"wait_for_acceptance": True}) %}

    return ();
}
```
