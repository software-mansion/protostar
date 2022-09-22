# `deploy_contract`

```python
def deploy_contract(
    contract_path: str,
    constructor_calldata: Optional[Union[List[int], Dict]] = None,
    *,
    config: Optional[CheatcodeNetworkConfig] = None
) -> DeployedContact:

class DeployedContract:
    contract_address: int
```
Deploys a contract given a path relative to a Protostar project root. The section [Deploying contracts from tests](../01-deploying-contracts.md) demonstrates a usage of this cheatcode.

`config` is a keyword only argument kept for compatibility with the migration [deploy_contract cheatcode](../../06-deploying/02-migrations/deploy-contract.md). See related documentation for more information.

:::warning
Deploying a contract is a slow operation. If it's possible try using this cheatcode in the [`__setup__` hook](../README.md#setup-hooks).
:::

:::info
`deploy_contract` is just a syntactic sugar over executing cheatcodes `declare` -> `prepare` -> `deploy` separately, and it's what it does under the hood.
:::

:::tip
You can provide `constructor_calldata` as a dictionary to leverage [data transformer](./README.md#data-transformer).
:::
