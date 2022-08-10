# Network configuration
```python
class CheatcodeNetworkConfig(TypedDict):
    wait_for_acceptance: bool
    "Wait for transaction to be accepted on chain."
```

`CheatcodeNetworkConfig` stores configuration used in `declare` and `deploy_contract` cheatcodes.

It has no effect in the test environment, however it is kept for compatibility.

#### Default configuration:
```python
CheatcodeNetworkConfig(
    wait_for_acceptance=False
)
```
