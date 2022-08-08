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

The `config` parameter allows passing [network configuration](../03-network-config.md) data. See related documentation for more information.

## Example

```python
%lang starknet

@external
func up():
    %{ declare("./build/main.json") %}

    return ()
end

```