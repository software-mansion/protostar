# `declare`

```python
def declare(
    contract: str,
    *,
    config: Optional[NetworkConfig] = None
) -> DeclaredContract:

class DeclaredContract:
    class_hash: int
```

Sends a declare transaction.

- `contract` — A path to the **compiled** contract or a [contract name](../compiling#contract-name). If you provide a contract name, Protostar will look for it in the [compiled-contracts-dir](../../cli-reference.md#--compiled-contracts-dir-pathbuild).
- `config` — A keyword only argument that allows configuring transaction and network parameters (e.g. max fee). See [network config](./network-config.md) for more details on this argument.

## Example

```cairo
%lang starknet

@external
func up() {
    %{ declare("main", config={"wait_for_acceptance": True, "max_fee": "auto"}) %}

    return ();
}
```
