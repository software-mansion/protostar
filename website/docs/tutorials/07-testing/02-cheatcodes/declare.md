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
Declares contract given a path relative to a Protostar project root.

`config` is a keyword only argument kept for compatibility with the migration [declare cheatcode](../../06-deploying/02-migrations/declare.md). See related documentation for more information.
