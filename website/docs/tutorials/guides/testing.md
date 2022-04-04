# Testing

T.B.D.

## Asserts

Protostar ships with its own assert functions. They don't accept [implicit arguments](https://www.cairo-lang.org/docs/how_cairo_works/builtins.html?highlight=implicit%20arguments#implicit-arguments) compared to asserts from [`starkware.cairo.common.math`](https://github.com/starkware-libs/cairo-lang/blob/master/src/starkware/cairo/common/math.cairo). You can import Protostar asserts in the following way:

```cairo title="test_my_contract.cairo"
from protostar.asserts import (
    assert_eq, assert_not_eq, assert_signed_lt, assert_signed_le, assert_signed_gt,
    assert_unsigned_lt, assert_unsigned_le, assert_unsigned_gt, assert_signed_ge,
    assert_unsigned_ge)
```

:::info
If your IDE supports Cairo and doesn't know how to import `protostar`, add the following directory
`$(which protostar)/../cairo` to the [`CAIRO_PATH`](https://www.cairo-lang.org/docs/how_cairo_works/imports.html?highlight=cairo_path).
:::

You can find all [assert signatures here](https://github.com/software-mansion/protostar/blob/master/cairo/protostar/asserts.cairo).

## Cheatcodes

Most of the time, testing smart contracts with assertions only is not enough. Some test cases require manipulating the state of the blockchain, as well as checking for reverts and events. For that reason, Protostar provides a set of cheatcodes.

Cheatcodes are available inside of [Cairo hints](https://www.cairo-lang.org/docs/hello_cairo/program_input.html#hints). You don't have to import anything. When Protostar runs tests, it replaces some core elements in [cairo-lang](https://pypi.org/project/cairo-lang/) library and inject cheatcodes to the hint scope.

:::note
If you are familiar with [Foundry](https://book.getfoundry.sh/forge/cheatcodes.html), you will recognize most cheatcodes.
:::

### `mock_call`

```python
def mock_call(contract_address: int, fn_name: str, ret_data: List[int]) -> None: ...
```

Mocks all calls to function with the name `fn_name` of a contract with an address `contract_address` unless [`clear_mock_call`](#clear_mock_call) is used. Mocked call returns data provided in `ret_data`.

#### Representing different data structures in `ret_data`

To use `mock_call` effectively, you need to understand how Cairo data structures are represented under the hood. `Cairo-lang` operates on list of integers. The following examples demonstrate how each data structure is represented in Python code.

```cairo title="Fixtures and type definitions"
const EXTERNAL_CONTRACT_ADDRESS = 0x3fe90a1958bb8468fb1b62970747d8a00c435ef96cda708ae8de3d07f1bb56b

struct Point:
    member x : felt
    member y : felt
end

@contract_interface
namespace ITestContract:
    func get_felt() -> (res : felt):
    end

    func get_array() -> (res_len : felt, res : felt*):
    end

    func get_struct() -> (res : Point):
    end
end
```

##### Felt

```cairo title="mocked_call returns a felt"
@view
func test_mock_call_returning_felt{syscall_ptr : felt*, range_check_ptr}():
  tempvar external_contract_address = EXTERNAL_CONTRACT_ADDRESS

  %{ mock_call(ids.external_contract_address, "get_felt", [42]) %}
  let (res) = ITestContract.get_felt(EXTERNAL_CONTRACT_ADDRESS)

  assert res = 42
  return ()
end
```

##### Array

To mock a function returning an array, provide data in the following format to `ret_data`:

```python title="Python representation of a Cairo array"
[n, value_1, value_2, ..., value_n]
```

```cairo title="mocked_call returns an array"
@view
func test_mock_call_returning_array{syscall_ptr : felt*, range_check_ptr}():
  tempvar external_contract_address = EXTERNAL_CONTRACT_ADDRESS

  %{ mock_call(ids.external_contract_address, "get_array", [1, 42]) %}
  let (res_len, res_arr) = ITestContract.get_array(EXTERNAL_CONTRACT_ADDRESS)

  assert res_arr[0] = 42
  return ()
end
```

##### Struct

```cairo title="mocked_call returns a struct"
@view
func test_mock_call_returning_struct{syscall_ptr : felt*, range_check_ptr}():
  tempvar external_contract_address = EXTERNAL_CONTRACT_ADDRESS

  %{ mock_call(ids.external_contract_address, "get_struct", [21,37]) %}
  let (res_struct) = ITestContract.get_struct(EXTERNAL_CONTRACT_ADDRESS)

  assert res_struct.x = 21
  assert res_struct.y = 37
  return ()
end
```

### `clear_mock_call`

```python
def clear_mock_call(contract_address: int, fn_name: str) -> None: ...
```

Removes a mocked call specified by a function name (`fn_name`) of a contract with an address (`contract_address`).

### `expect_revert`

```python
def expect_revert() -> None: ...
```

If a code beneath `expect_revert` triggers revert, a test will pass.

```cairo title="This test passes despite using a random contract address."
@external
func test_call_to_non_existing_contract{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    local contract_a_address : felt
    %{ ids.contract_a_address = 0101010101010101010101010 %}

    %{ expect_revert() %}
    BasicContract.increase_balance(contract_address=contract_a_address, amount=3)
    return ()
end
```

### `deploy_contract`

```python
def deploy_contract(contract_path: str) -> Contract:
```

T.B.D.

### `start_prank`

```python
def start_prank(caller_address: int) -> None: ...
```

Changes caller address until [`stop_prank`](#stop_prank) cheatcode is used.

### `stop_prank`

```python
def stop_prank() -> None: ...
```

Resets caller address. Always used with [`start_prank`](#start_prank).

### `roll`

```python
def roll(blk_number: int) -> None: ...
```

Sets block number.

### `warp`

```python
def warp(blk_timestamp: int) -> None: ...
```

Sets block timestamp.
