# `deploy_contract`

```python
def deploy_contract(
    self,
    class_hash: str | int,
    constructor_args: list[int] | dict[str, Any] | None = None,
    *,
    config: Optional[CheatcodeNetworkConfig] = None
) -> DeployedContract: ...

@dataclass(frozen=True)
class DeployedContract:
    contract_address: int
```

Deploys a contract to the network.
- `contract` — A path to the **compiled** contract or a [contract name](../compiling#contract-name). If you provide a contract name, Protostar will look for it in the [compiled-contracts-dir](../../cli-reference.md#--compiled-contracts-dir-pathbuild).
- `constructor_args` — Arguments to the constructor. It can be either a list of felts or a dictionary. To use [data transformer](../testing/cheatcodes#data-transformer), provide a dictionary.
- `config` — A keyword only argument that allows configuring transaction and network parameters (e.g. max fee). See [network config](./network-config.md) for more details on this argument.

## Example

```cairo
%lang starknet

@external
func up() {
    %{ deploy_contract("main", config={"wait_for_acceptance": True}) %}

    return ();
}
```
