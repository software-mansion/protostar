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
Declares contract given a path relative to a Protostar project root.

[More information about `config`](../../deploying/network_config).
