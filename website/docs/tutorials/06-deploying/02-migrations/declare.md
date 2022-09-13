# `declare`

```python
def declare(
    contract_path: str,
    *,
    config: Optional[CheatcodeNetworkConfig] = None
) -> DeclaredContract:

class DeclaredContract:
    class_hash: int
```
Declares contract given a relative to a project root path to **compiled** contract.

`config` is a keyword only argument that allows passing [network configuration](../03-network-config.md) data. See related documentation for more information.

## Example

```cairo
%lang starknet

@external
func up() {
    %{ declare("./build/main.json", config={"wait_for_acceptance": True}) %}

    return ();
}
```
