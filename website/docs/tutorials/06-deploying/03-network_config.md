---
sidebar_label: Network config
---
# Network config

It is as a dictionary storing the config for network related cheatcodes (`declare`, `deploy`, `deploy_contract`).

It has no effect in the test environment, however it is kept for compatibility.

#### Parameters:
```python
wait_for_acceptance: bool # Wait until "Accepted on L2" status.
```

#### Default config:
```python
{
    "wait_for_acceptance": False
}
