# `deploy_contract`

```python
def deploy_contract(
    contract_path: str,
    constructor_calldata: Optional[Union[List[int], Dict]] = None,
    *,
    config: Optional[NetworkConfig] = None
) -> DeployedContact:

class DeployedContract:
    contract_address: int
```
Deploys a contract given a path relative to a Protostar project root. The section [Deploying contracts from tests](../01-deploying-contracts.md) demonstrates a usage of this cheatcode.

The `config` parameter allows passing [network configuration](../../06-deploying/03-network-config.md) data. See related documentation for more information.

:::warning
Deploying a contract is a slow operation. If it's possible try using this cheatcode in the [`__setup__` hook](../README.md#__setup__).
:::

:::info
`deploy_contract` is just a syntactic sugar over executing cheatcodes `declare` -> `prepare` -> `deploy` separately, and it's what does it under the hood.
:::

:::tip
You can provide `constructor_calldata` as a dictionary to leverage [data transformer](./README.md#data-transformer).
:::
