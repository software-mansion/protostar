# `deploy`

```python
def deploy(
    prepared: PreparedContract,
) -> DeployedContract:

class DeployedContract:
    contract_address: int
```
Deploys contract for deployment given `PreparedContract`.

:::warning
You can't deploy the same `PreparedContract` twice.
:::

```cairo title="./src/main.cairo"
@constructor
func constructor(initial_balance : Uint256, contract_id : felt):
    # ...
    return ()
end
```

:::info
To learn more how data is transformed from Python to Cairo read [Data transformation section in the Starknet.py's documentation](https://starknetpy.readthedocs.io/en/latest/guide.html#data-transformation).
:::
