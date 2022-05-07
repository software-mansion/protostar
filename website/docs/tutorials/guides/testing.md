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
```code title="tests/test_utils.cairo"
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

:::info
In the example above, Protostar will run every test case it manages to find in the `tests` directory. You can read more about specifying where and how Protostar should search for test cases by running `protostar test --help`. 
:::

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
from starkware.cairo.common.uint256 import Uint256, uint256_add

# Define a storage variable.
@storage_var
func balance() -> (res : Uint256):
end

@storage_var
func id() -> (res : felt):
end


# Increases the balance by the given amount.
@external
func increase_balance{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(amount: Uint256):
    let (read_balance) = balance.read()
    let (new_balance, carry) = uint256_add(read_balance, amount)
    assert carry = 0
    balance.write(new_balance)
    return ()
end

# Returns the current balance.
@view
func get_balance{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}() -> (
        res : Uint256):
    let (res) = balance.read()
    return (res)
end

@view
func get_id{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}() -> (res : felt):
    let (res) = id.read()
    return (res)
end

@constructor
func constructor{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(initial_balance: Uint256, _id: felt):
    balance.write(initial_balance)
    id.write(_id)
    return ()
end

```
Then we can create a test case for the contract.
Inside `tests` directory, create a `test_storage.cairo` file.
```code title="tests/test_storage.cairo"
%lang starknet

@contract_interface
namespace StorageContract:
    func increase_balance(amount : Uint256):
    end

    func get_balance() -> (res : Uint256):
    end
    
    func get_id() -> (res: felt):
    end
end

@external
func test_proxy_contract{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    local contract_a_address : felt
    # We deploy contract and put its address into a local variable. Second argument is calldata array
    %{ ids.contract_a_address = deploy_contract("./src/commands/test/examples/basic_with_constructor.cairo", [100, 0, 1]).contract_address %}

    let (res) = StorageContract.get_balance(contract_address=contract_a_address)
    assert res.low = 100
    assert res.high = 0

    let (id) = StorageContract.get_id(contract_address=contract_a_address)
    assert id = 1
  
    StorageContract.increase_balance(
        contract_address=contract_address,
        amount=Uint256(50, 0)
    )

    let (res) = StorageContract.get_balance(contract_address=contract_address)
    assert res.low = 150
    assert res.high = 0
    return ()
end
```

:::info
Please refer to ["passing typles and structs in calldata"](https://www.cairo-lang.org/docs/hello_starknet/more_features.html#passing-tuples-and-structs-in-calldata) on how to serialize your constructor arguments to array of integers
:::

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

To use `mock_call` effectively, you need to understand how Cairo data structures are represented under the hood. `Cairo-lang` operates on a list of integers. The following examples demonstrate how each data structure is represented in Python code.


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
def expect_revert(error_type: Optional[str] = None, error_message: Optional[str] = None) -> None: ...
```

If a code beneath `expect_revert` raises a specified exception, a test will pass. If not, a test will fail.

:::info
Protostar displays an error type and a message when a test fails.
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
func test_failing_to_call_external_contract{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    %{ expect_revert("UNINITIALIZED_CONTRACT") %}
    BasicContract.increase_balance(contract_address=21, amount=3)

    return ()
end
```


```cairo title="Use 'error_message' to check the last error annotation."
%lang starknet

func inverse(x) -> (res):
    with_attr error_message("x must not be zero. Got x={x}."):
        return (res=1 / x)
    end
end

func assert_not_equal(a, b):
    let diff = a - b
    with_attr error_message("a and b must be distinct."):
        inverse(diff)
    end
    return ()
end

@view
func test_error_message{syscall_ptr : felt*, range_check_ptr}():
    %{ expect_revert(error_message="a and b must be distinct.") %}
    assert_not_equal(0, 0)
    return ()
end
```

:::info
Use [scope attributes](https://www.cairo-lang.org/docs/how_cairo_works/scope_attributes.html?highlight=with_attr) to annotate a code block with an informative error message.
:::

### `deploy_contract`

```python
def deploy_contract(contract_path: str, constructor_calldata: List[int]) -> DeployedContact:

class DeployedContract:
    @property
    def contract_address(self) -> int: ...
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
