# `declare`

```python
def declare(
    contract: str,
    *,
    config: Optional[DeclareCheatcodeNetworkConfig] = None
) -> DeclaredContract:

class DeclaredContract:
    class_hash: int
```

Sends a declare transaction.

- `contract` — A path to the **compiled** contract or a [contract name](../compiling#contract-name). If you provide a contract name, Protostar will look for it in the [compiled-contracts-dir](../../cli-reference.md#--compiled-contracts-dir-pathbuild).
- `config` — A keyword only argument that allows configuring transaction and network parameters.

## `DeclareCheatcodeNetworkConfig`
```python
class DeclareCheatcodeNetworkConfig(CheatcodeNetworkConfig):
    max_fee: NotRequired[Wei | "auto"]
```
- `max_fee` — The maximum fee that the sender is willing to pay for the transaction. Required for transactions V1.

This dictionary inherits properties from [CheatcodeNetworkConfig](./network-config).

## Example

```cairo
%lang starknet

@external
func up() {
    %{ declare("main", config={"wait_for_acceptance": True, "max_fee": "auto"}) %}

    return ();
}
```
