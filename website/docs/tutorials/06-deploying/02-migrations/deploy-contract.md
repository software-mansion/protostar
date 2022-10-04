# `deploy_contract`

```python
def deploy_contract(
    self,
    contract: str,
    constructor_args: list[int] | dict[str, Any] | None = None,
    *,
    config: Optional[CheatcodeNetworkConfig] = None
) -> DeployedContract: ...

@dataclass(frozen=True)
class DeployedContract:
    contract_address: int
```
:::warning Depreciation warning
This cheatcode will not be supported in the future. Use [declare](./declare.md) and [invoke](./invoke.md) cheatcodes instead.
:::

Deploys a contract to the network.
- `contract` — A path to the **compiled** contract or a contract name. If you provide a contract name, Protostar will search for the compiled contract in the default build output (which is `build` in the root of the project) directory.
- `constructor_args` — Arguments to the constructor. It can be either a list of felts or a dictionary. To use [data transformer](../../testing/cheatcodes#data-transformer), provide a dictionary.
- `config` — A keyword only argument that allows passing [network configuration](../03-network-config.md).




## Example

```cairo
%lang starknet

@external
func up() {
    %{ deploy_contract("main", config={"wait_for_acceptance": True}) %}

    return ();
}
```
