# `declare`

```python
def declare(
    contract_path_str: str,
    *,
    config: Optional[DeclareCheatcodeNetworkConfig] = None
) -> DeclaredContract:

class DeclaredContract:
    class_hash: int
```

Sends a declare transaction.

- `contract_path_str` — A path to the **compiled** contract or a [contract name](../../compiling#contract-name). If you provide a contract name, Protostar will compile the contract to the migration output directory.
- `config` — A keyword only argument that allows configuring transaction and network parameters.

## `DeclareCheatcodeNetworkConfig`
```python
class DeclareCheatcodeNetworkConfig(CheatcodeNetworkConfig):
    max_fee: NotRequired[Wei]
```
- `max_fee` — The maximum fee that the sender is willing to pay for the transaction.

This dictionary inherits properties from [CheatcodeNetworkConfig](../03-network-config.md).

## Example

```cairo
%lang starknet

@external
func up() {
    %{ declare("main", config={"wait_for_acceptance": True}) %}

    return ();
}
```
