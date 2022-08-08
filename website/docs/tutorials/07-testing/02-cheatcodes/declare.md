# `declare`

```python
def declare(
    contract_path: str,
    *,
    config: Optional[NetworkConfig] = None
) -> DeclaredContract:

class DeclaredContract:
    class_hash: int
```
Declares contract given a path relative to a Protostar project root.

The `config` parameter allows passing [network configuration](../../06-deploying/03-network-config.md) data. See related documentation for more information.
