# `deploy_contract`

```python
def deploy_contract(
    self,
    contract_path: str,
    constructor_args: Optional[List[int]] = None,
) -> DeployedContract: ...

@dataclass(frozen=True)
class DeployedContract:
    contract_address: int
```


Deploys a **compiled** contract given a path relative to the project root.


:::warning
Don't use `starkware.starknet.common.syscalls.deploy`. It will deploy the contract to the Protostar's local StarkNet.
:::




## Example

```cairo
%lang starknet

@external
func up():
    %{ deploy_contract("./build/main.json") %}

    return ()
end
```