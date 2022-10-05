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

- `contract` — A path to the **compiled** contract or a contract name. If you provide a contract name, Protostar will search for the compiled contract in the default build output (which is `build` in the root of the project) directory.
- `config` — A keyword only argument kept for compatibility with the migration [declare cheatcode](../../06-deploying/02-migrations/declare.md). See related documentation for more information.
