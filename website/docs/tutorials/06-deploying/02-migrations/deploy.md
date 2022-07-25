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




## Example

```cairo
%lang starknet

@external
func up():
    %{ deploy_contract("./build/main.json") %}

    return ()
end
```