# `deploy`

```python
def deploy(
    prepared: PreparedContract,
    *,
    config: Optional[CheatcodeNetworkConfig] = None
) -> DeployedContract:

class DeployedContract:
    contract_address: int
```
Deploys contract for deployment given `PreparedContract`.

The `config` parameter allows passing [network configuration](../../06-deploying/03-network-config.md) data. See related documentation for more information.

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
