# `declare`

```python
def declare(
    contract_path: str,
    *args,
    config: Optional[Dict[str, Any]] = None
) -> DeclaredContract:

class DeclaredContract:
    class_hash: int
```
Declares contract given a relative to a project root path to **compiled** contract.

[More information about `config`](../network_config).

## Example

```python
%lang starknet

@external
func up():
    %{ declare("./build/main.json") %}

    return ()
end

```