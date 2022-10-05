# `deploy_contract`

```python
def deploy_contract(
    self,
    contract_path: str,
    constructor_args: list[int] | dict[str, Any] | None = None,
    *,
    config: Optional[CheatcodeNetworkConfig] = None
) -> DeployedContract: ...

@dataclass(frozen=True)
class DeployedContract:
    contract_address: int
```
:::warning
This cheatcode will be removed once [StarkNet drops support for deploy transaction](https://docs.starknet.io/documentation/develop/Blocks/transactions/#deploy_transaction).  
:::

Deploys a contract to the network.
- `contract_path` — A path to the **compiled** contract or a contract name. If you provide a contract name, Protostar will compile the contract to the migration output directory.
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
