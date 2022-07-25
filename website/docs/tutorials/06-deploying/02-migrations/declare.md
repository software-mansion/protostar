# `declare`

```python
def declare(contract_path: str) -> DeclaredContract:

class DeclaredContract:
    class_hash: int
```
Declares contract given a relative to a project root path to **compiled** contract.

:::info
This cheatcode has testing counterpart — [declare](/docs/tutorials/testing/cheatcodes/declare).
:::


## Example

```python
%lang starknet

@external
func up():
    %{ declare("./build/main.json") %}

    return ()
end

```