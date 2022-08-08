# Network configuration
```python
class NetworkConfig(TypedDict):
    wait_for_acceptance: bool
    "Wait for transaction to be accepted on chain."
```

`NetworkConfig` stores configuration used in `declare`, `deploy` and `deploy_contract` cheatcodes.

It has no effect in the test environment, however it is kept for compatibility.

#### Default configuration:
```python
NetworkConfig(
    wait_for_acceptance=False
)
```
