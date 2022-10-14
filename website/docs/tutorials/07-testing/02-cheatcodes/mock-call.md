# `mock_call`

```python
def mock_call(contract_address: int, fn_name: str, ret_data: Union[List[int], Dict]) -> Callable: ...
```

Mocks all calls to function with the name `fn_name` of a contract with an address `contract_address`, until the returned callable is called. 

Mocked call returns data provided in `ret_data`.

Mock works globally, for all contracts, not only the testing contract.

## Caveats
- Mock call only works for functions that are in the contract ABI. It does not mock any internal function calls, even if the function name and parameter types match.

:::tip
You can provide constructor arguments as a dictionary to leverage [data transformer](README.md#data-transformer).
:::

## Representing different data structures in `ret_data`

To use `mock_call` effectively, you need to understand how Cairo data structures are represented under the hood. `Cairo-lang` operates on a list of integers. The following examples demonstrate how each data structure is represented in Python code.


### Felt

```cairo title="mocked_call returns a felt"
%lang starknet

@contract_interface
namespace ITestContract {
    func get_felt() -> (res: felt) {
    }
}

const EXTERNAL_CONTRACT_ADDRESS = 0x3fe90a1958bb8468fb1b62970747d8a00c435ef96cda708ae8de3d07f1bb56b;

@external
func test_mock_call_returning_felt{syscall_ptr: felt*, range_check_ptr}() {
    tempvar external_contract_address = EXTERNAL_CONTRACT_ADDRESS;

    %{ stop_mock = mock_call(ids.external_contract_address, "get_felt", [42]) %}
    let (res) = ITestContract.get_felt(EXTERNAL_CONTRACT_ADDRESS);
    %{ stop_mock() %}

    assert res = 42;
    return ();
}
```

### Array

To mock a function returning an array, provide data in the following format to `ret_data`:

```python title="Python representation of a Cairo array"
[n, value_1, value_2, ..., value_n]
```

```cairo title="mocked_call returns an array"
%lang starknet

@contract_interface
namespace ITestContract {
    func get_array() -> (res_len: felt, res: felt*) {
    }
}

const EXTERNAL_CONTRACT_ADDRESS = 0x3fe90a1958bb8468fb1b62970747d8a00c435ef96cda708ae8de3d07f1bb56b;

@external
func test_mock_call_returning_array{syscall_ptr: felt*, range_check_ptr}() {
    tempvar external_contract_address = EXTERNAL_CONTRACT_ADDRESS;

    %{ stop_mock = mock_call(ids.external_contract_address, "get_array", [1, 42]) %}
    let (res_len, res_arr) = ITestContract.get_array(EXTERNAL_CONTRACT_ADDRESS);
    %{ stop_mock() %}

    assert res_arr[0] = 42;
    return ();
}
```

### Struct

```cairo title="mocked_call returns a struct"
%lang starknet

struct Point {
    x: felt,
    y: felt,
}

@contract_interface
namespace ITestContract {
    func get_struct() -> (res: Point) {
    }
}

const EXTERNAL_CONTRACT_ADDRESS = 0x3fe90a1958bb8468fb1b62970747d8a00c435ef96cda708ae8de3d07f1bb56b;

@external
func test_mock_call_returning_struct{syscall_ptr: felt*, range_check_ptr}() {
    tempvar external_contract_address = EXTERNAL_CONTRACT_ADDRESS;

    %{ stop_mock = mock_call(ids.external_contract_address, "get_struct", [21,37]) %}
    let (res_struct) = ITestContract.get_struct(EXTERNAL_CONTRACT_ADDRESS);
    %{ stop_mock() %}

    assert res_struct.x = 21;
    assert res_struct.y = 37;
    return ();
}
```
