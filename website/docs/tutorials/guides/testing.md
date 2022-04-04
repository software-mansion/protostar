---
sidebar_label: Testing (6 min)
---

# Testing
Protostar provides a flexible testing environment for Cairo smart contracts. 
It allows to write unit/integration tests with a help of [cheatcodes](#cheatcodes).

## Unit testing
We will start with a [just created protostar project](/docs/tutorials/project-initialization).
In your `src` directory create a `utils.cairo` file
```code title="src/utils.cairo"
func sum_func{syscall_ptr : felt*, range_check_ptr}(a : felt, b : felt) -> (res : felt):
    return (a+b)
end
```
This is our target function, which we are going to test.
Then in the `tests` directory create file `test_utils.cairo`, which contains a single test case.
```code title="src/test_utils.cairo"
%lang starknet

from src.utils import sum_func

@external
func test_sum{syscall_ptr : felt*, range_check_ptr}():
    let (r) = sum_func(4,3)
    assert r = 7
    return ()
end
```

Then run your test with
```
protostar test ./tests
```

```console title="expected result"
Collected 1 items

test_utils: .
----- TEST SUMMARY ------
1 passed
Ran 1 out of 1 total tests
```

:::info
You can place your test files anywhere you want. Protostar recursively searches 
the given directory for cairo files with a name starting with `test_` and treats them as tests files. 
All functions inside a test file starting with `test_` are treated as separeate test cases.
:::

## Deploying contracts from tests

For most projects such testing of isolated functions won't be enough. Protostar provides a [`deploy_contract` cheatcode](#deploy_contract) to test interactions between contracts.
We will use an example of a simple storage contract to show you how to deploy contract inside a test case.

First, inside a `src` directory, create a `storage_contract.cairo`
```code title="src/storage_contract.cairo"
%lang starknet
%builtins pedersen range_check

from starkware.cairo.common.cairo_builtins import HashBuiltin

# Define a storage variable.
@storage_var
func balance() -> (res : felt):
end

# Increases the balance by the given amount.
@external
func increase_balance{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(amount: felt):
    let (res) = balance.read()
    balance.write(res + amount)
    return ()
end

# Returns the current balance.
@view
func get_balance{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}() -> (
        res : felt):
    let (res) = balance.read()
    return (res)
end
```
Then we can create a test case for the contract.
Inside `tests` directory, create a `test_storage.cairo` file.
```code title="tests/test_storage.cairo"
%lang starknet

@contract_interface
namespace StorageContract:
    func increase_balance(amount : felt):
    end

    func get_balance() -> (res : felt):
    end
end

@external
func test_proxy_contract{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    local contract_address : felt
    %{
        # We deploy contract and put its address into a local variable
        ids.contract_address = deploy_contract("./src/storage_contract.cairo").contract_address 
    %}

    StorageContract.increase_balance(
        contract_address=contract_address,
        amount=5
    )

    let (res) = StorageContract.get_balance(contract_address=contract_address)
    assert res = 5
    return ()
end
```

Then run your test with
```
protostar test ./tests
```

```console title="expected result"
Collected 2 items

storage_test: .
test_utils: .
----- TEST SUMMARY ------
2 passed
Ran 2 out of 2 total tests
```

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


##### Felt

```cairo title="mocked_call returns a felt"
%lang starknet

@contract_interface
namespace ITestContract:
    func get_felt() -> (res : felt):
    end
end

const EXTERNAL_CONTRACT_ADDRESS = 0x3fe90a1958bb8468fb1b62970747d8a00c435ef96cda708ae8de3d07f1bb56b

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
%lang starknet

@contract_interface
namespace ITestContract:
    func get_array() -> (res_len : felt, res : felt*):
    end
end

const EXTERNAL_CONTRACT_ADDRESS = 0x3fe90a1958bb8468fb1b62970747d8a00c435ef96cda708ae8de3d07f1bb56b

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
%lang starknet

struct Point:
    member x : felt
    member y : felt
end

@contract_interface
namespace ITestContract:
    func get_struct() -> (res : Point):
    end
end

const EXTERNAL_CONTRACT_ADDRESS = 0x3fe90a1958bb8468fb1b62970747d8a00c435ef96cda708ae8de3d07f1bb56b

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
def expect_revert(error_type: str = ".*", error_message: str = ".*") -> Callable[[], None]: ...
```

If a code beneath `expect_revert` raises a specified exception, a test will pass. If not, a test will fail. It accepts regex `error_type` and `error_message` and returns a function that limits the scope. Calling that function is optional.

:::info
Protostar displays an error type and message when a test fails.
:::

```cairo title="This test passes despite calling an uninitialized contract."
%lang starknet

@contract_interface
namespace BasicContract:
    func increase_balance(amount : felt):
    end

    func get_balance() -> (res : felt):
    end
end

@external
func test_call_not_existing_contract{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    local contract_a_address : felt
    %{ ids.contract_a_address = 3421347281347298134789213489213 %}

    %{ expect_revert("UNINITIALIZED_CONTRACT") %}
    BasicContract.increase_balance(contract_address=contract_a_address, amount=3)
    return ()
end
```


```cairo title="This test 'fails' because the exceptions wasn't thrown."
@external
func test_fail_error_was_not_raised_before_stopping_expect_revert{
        syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    %{ stop_expecting_revert = expect_revert("UNINITIALIZED_CONTRACT") %}
    local contract_a_address = 42
    %{ stop_expecting_revert() %}

    return ()
end
```

:::info
The prefix `test_fail_` tells Protostar to pass the test if it fails and fail if it passes.
:::

### `deploy_contract`

```python
def deploy_contract(contract_path: str) -> DeployedContact:

class DeployedContact:
    contract_address: str
```
Deploys a contract given a path relative to a Protostar project root. The section [Deploying contracts from tests](#deploying-contracts-from-tests) demonstrates a usage of this cheatcode.


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
