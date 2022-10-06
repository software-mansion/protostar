# `declare`

```python
def declare(
    contract: str,
    *,
    config: Optional[CheatcodeNetworkConfig] = None
) -> DeclaredContract:

class DeclaredContract:
    class_hash: int
```
Declares contract given a path relative to a Protostar project root.

- `contract` — A path to the contract's main `.cairo` source file.
- `config` — A keyword only argument kept for compatibility with the migration [declare cheatcode](../../06-deploying/02-migrations/declare.md). See related documentation for more information.
