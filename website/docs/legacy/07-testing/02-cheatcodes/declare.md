# `declare`

```python
def declare(contract: str) -> DeclaredContract:

class DeclaredContract:
    class_hash: int
```
Declares contract given a path relative to a Protostar project root.

- `contract` — A path to the contract's main `.cairo` source file.