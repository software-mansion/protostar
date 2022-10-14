# `call`

```python
def call(
    contract_address: int,
    function_name: str,
    inputs: list[int] | dict[str, Any] | None = None,
) -> ContractCallResult:

class ContractCallResult(NamedTuple):
    ...
```
Calls a StarkNet contract without affecting the StarkNet's state.

:::tip
You can provide `inputs` as a dictionary to use [data transformer](./README.md#data-transformer).
:::


## Example

```shell
protostar migrate migrations/migration_01.cairo
    --network testnet
    --output-dir migrations/output
```

```cairo title="migrations/migration_01.cairo"
%lang starknet

@external
func up() {
    %{
        contract_address = deploy_contract("./build/main.json").contract_address

        result = call(contract_address, "identity", {"arg": 42})

        assert result.res == 42
    %}

    return ();
}
```

```cairo title="src/main.cairo"
%lang starknet

@view
func identity(arg) -> (res: felt) {
    return (arg,);
}
```
