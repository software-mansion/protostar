---
sidebar_label: Testing
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

:::tip
If you experience any errors during test collection phase consider using `--safe-collecting` flag.
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
All functions inside a test file starting with `test_` are treated as separate test cases.
:::

:::warning
The tested file cannot have a constructor that expects arguments because, Protostar won't be able to deploy the contract automatically. As a workaround, keep your constructor in a different file. You can test the constructor using the `deploy_contract` cheatcode as described below.
:::
## Deploying contracts from tests

For most projects such testing of isolated functions won't be enough. Protostar provides a [`deploy_contract` cheatcode](#deploy_contract) to test interactions between contracts.
We will use an example of a simple storage contract to show you how to deploy contract inside a test case.

First, inside a `src` directory, create a `storage_contract.cairo`
```code title="src/storage_contract.cairo"
%lang starknet

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
func increase_balance{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        amount : Uint256):
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
func constructor{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        initial_balance : Uint256, _id : felt):
    balance.write(initial_balance)
    id.write(_id)
    return ()
end

```
Then we can create a test case for the contract.
Inside `tests` directory, create a `test_storage_contract.cairo` file.
```code title="tests/test_storage_contract.cairo"
%lang starknet
from starkware.cairo.common.uint256 import Uint256

@contract_interface
namespace StorageContract:
    func increase_balance(amount : Uint256):
    end

    func get_balance() -> (res : Uint256):
    end

    func get_id() -> (res : felt):
    end
end

@external
func test_proxy_contract{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    local contract_address : felt
    # We deploy contract and put its address into a local variable. Second argument is calldata array
    %{ ids.contract_address = deploy_contract("./src/storage_contract.cairo", [100, 0, 1]).contract_address %}

    let (res) = StorageContract.get_balance(contract_address=contract_address)
    assert res.low = 100
    assert res.high = 0

    let (id) = StorageContract.get_id(contract_address=contract_address)
    assert id = 1

    StorageContract.increase_balance(contract_address=contract_address, amount=Uint256(50, 0))

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

## `__setup__`
Often while writing tests you have some setup work that needs to happen before tests run. The hook `__setup__` can simplify and speed up your tests. Use `context` variable to pass data from `__setup__` to test functions as demonstrated on the example below:

```cairo
%lang starknet

@external
func __setup__():
    %{ context.contract_a_address = deploy_contract("./tests/integration/testing_hooks/basic_contract.cairo").contract_address %}
    return ()
end

@external
func test_something():
    tempvar contract_address
    %{ ids.contract_address = context.contract_a_address %}

    # ...

    return ()
end
```


:::info
Protostar executes `__setup__` only once per a [test suite](https://en.wikipedia.org/wiki/Test_suite). Then, for each test case Protostar copies the StarkNet state and `context` object.
:::




## Cheatcodes

Most of the time, testing smart contracts with assertions only is not enough. Some test cases require manipulating the state of the blockchain, as well as checking for reverts and events. For that reason, Protostar provides a set of cheatcodes.

Cheatcodes are available inside of [Cairo hints](https://www.cairo-lang.org/docs/hello_cairo/program_input.html#hints). You don't have to import anything. When Protostar runs tests, it replaces some core elements in [cairo-lang](https://pypi.org/project/cairo-lang/) library and inject cheatcodes to the hint scope.

:::note
If you are familiar with [Foundry](https://book.getfoundry.sh/forge/cheatcodes.html), you will recognize most cheatcodes.
:::

### `mock_call`

```python
def mock_call(contract_address: int, fn_name: str, ret_data: Union[List[int], Dict]) -> Callable: ...
```

Mocks all calls to function with the name `fn_name` of a contract with an address `contract_address` until the returned callable is called. Mocked call returns data provided in `ret_data`. Mock works globally, for all of the contracts, not only the testing contract.

:::tip
You can provide constructor arguments as a dictionary to leverage [data transformer](/docs/tutorials/guides/testing#data-transformer).
:::

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

@external
func test_mock_call_returning_felt{syscall_ptr : felt*, range_check_ptr}():
  tempvar external_contract_address = EXTERNAL_CONTRACT_ADDRESS

  %{ stop_mock = mock_call(ids.external_contract_address, "get_felt", [42]) %}
  let (res) = ITestContract.get_felt(EXTERNAL_CONTRACT_ADDRESS)
  %{ stop_mock() %}

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

@external
func test_mock_call_returning_array{syscall_ptr : felt*, range_check_ptr}():
  tempvar external_contract_address = EXTERNAL_CONTRACT_ADDRESS

  %{ stop_mock = mock_call(ids.external_contract_address, "get_array", [1, 42]) %}
  let (res_len, res_arr) = ITestContract.get_array(EXTERNAL_CONTRACT_ADDRESS)
  %{ stop_mock() %}

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

@external
func test_mock_call_returning_struct{syscall_ptr : felt*, range_check_ptr}():
  tempvar external_contract_address = EXTERNAL_CONTRACT_ADDRESS

  %{ stop_mock = mock_call(ids.external_contract_address, "get_struct", [21,37]) %}
  let (res_struct) = ITestContract.get_struct(EXTERNAL_CONTRACT_ADDRESS)
  %{ stop_mock() %}

  assert res_struct.x = 21
  assert res_struct.y = 37
  return ()
end
```

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


```cairo title="'except_revert' checks if the last error annotation contains 'error_message'."
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

@external
func test_error_message{syscall_ptr : felt*, range_check_ptr}():
    %{ expect_revert(error_message="must be distinct") %}
    assert_not_equal(0, 0)
    return ()
end
```

:::tip
Use [scope attributes](https://www.cairo-lang.org/docs/how_cairo_works/scope_attributes.html?highlight=with_attr) to annotate a code block with an informative error message.
:::

### `expect_events`
```python
 def expect_events(
            *raw_expected_events: Union[
                str, # Protostar interprets string as an event's name 
                TypedDict("ExpectedEvent", {
                    "name": str,
                    "data": NotRequired[Union[
                      List[int],
                      Dict[
                        # e.g.
                        # {"current_balance" : 37, "amount" : 21}
                        # 
                        # for the following event signature:
                        # @event
                        # func balance_increased(current_balance : felt, amount : felt):
                        # end
                        DataTransformer.ArgumentName,
                        DataTransformer.SupportedType,
                      ]
                    ]],
                    "from_address": NotRequired[int]
                },
            )],
        ) -> None: ...
```
Compares expected events with events in the StarkNet state. You can use this cheatcode to test whether a contract emits specified events. Protostar compares events after a test case is completed. Therefore, you can use this cheatcode in any place within a test case.

:::tip
You can provide `"data"` as a dictionary to leverage [data transformer](/docs/tutorials/guides/testing#data-transformer).
:::

```cairo title="Protostar also checks the order of emitted events."
%lang starknet

@event
func foobar(number : felt):
end

func emit_foobar{syscall_ptr : felt*, range_check_ptr}(number : felt):
    foobar.emit(number)
    return ()
end

@contract_interface
namespace BasicContract:
    func increase_balance():
    end
end

# ----------------------------------------------

@external
func test_expect_events_are_in_declared_order{syscall_ptr : felt*, range_check_ptr}():
    %{ expect_events({"name": "foobar", "data": [21]}, {"name": "foobar", "data": [37]}) %}
    emit_foobar(21)
    emit_foobar(37)
    return ()
end

@external
func test_expect_event_by_contract_address{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals
    local contract_address : felt
    %{
        ids.contract_address = deploy_contract("./src/commands/test/examples/cheats/expect_events/basic_contract.cairo").contract_address
        expect_events({"name": "balance_increased", "from_address": ids.contract_address})
    %}
    BasicContract.increase_balance(contract_address=contract_address)
    return ()
end
```

### `deploy_contract`

```python
def deploy_contract(contract_path: str, constructor_calldata: Optional[Union[List[int], Dict]] = None) -> DeployedContact:

class DeployedContract:
    contract_address: int
```
Deploys a contract given a path relative to a Protostar project root. The section [Deploying contracts from tests](#deploying-contracts-from-tests) demonstrates a usage of this cheatcode.

:::warning
Deploying a contract is a slow operation. If it's possible try using this cheatcode in the [`__setup__` hook](#__setup__).
:::

:::info
`deploy_contract` is just a syntactic sugar over executing cheatcodes `declare` -> `prepare` -> `deploy` separately, and it's what does it under the hood.
:::

:::tip
You can provide `constructor_calldata` as a dictionary to leverage [data transformer](/docs/tutorials/guides/testing#data-transformer).
:::

### `declare`

```python
def declare(contract_path: str) -> DeclaredContract:

class DeclaredContract:
    class_hash: int
```
Declares contract given a path relative to a Protostar project root.

### `prepare`
```python
def prepare(declared: DeclaredContract, constructor_calldata: Optional[Union[List[int], Dict]]] = None) -> PreparedContract:

class PreparedContract:
    constructor_calldata: List[int]
    contract_address: int
    class_hash: int
```
Prepares contract for deployment given `DeclaredContract` and constructor_calldata. The cheatcode is useful when you want to know contract address before deploying it to affect constructor with a targeted cheatcode. Example:

```
@external
func test_prank_constructor{syscall_ptr : felt*, range_check_ptr}():
    %{
        declared = declare("path/to/contract.cairo")
        prepared = prepare(declared, [1,2,3])
        start_prank(111, target_contract_address=prepared.contract_address)

        # constructor will be affected by prank
        deploy(prepared)
    %}
    return ()
end

```
:::info
You can prepare multiple contracts from one `DeclaredContract`.
:::

:::tip
You can provide `constructor_calldata` as a dictionary to leverage [data transformer](/docs/tutorials/guides/testing#data-transformer).
:::

### `deploy`
```
def deploy(prepared: PreparedContract) -> DeployedContract:

class DeployedContract:
    contract_address: int
```
Deploys contract for deployment given `PreparedContract`. 

:::warning
You can't deploy the same `PreparedContract` twice.
:::




```cairo title="./src/main.cairo"
@constructor
func constructor(initial_balance : Uint256, contract_id : felt):
    # ...
    return ()
end
```

:::info
To learn more how data is transformed from Python to Cairo read [Data transformation section in the Starknet.py's documentation](https://starknetpy.readthedocs.io/en/latest/guide.html#data-transformation).
:::



### `start_prank`

```python
def start_prank(caller_address: int, target_contract_address: Optional[int] = None) -> Callable: ...
```

Changes a caller address returned by `get_caller_address()` until the returned callable is called. If `target_contract_address` is specified, `start_prank` affects only the contract with the specified address. Otherwise, `start_prank` affects the current contract.

#### In unit tests
```cairo title="Local assert passes"

@external
func test_remote_prank{syscall_ptr : felt*, range_check_ptr}():
    %{ stop_prank_callable = start_prank(123) %}

    let (caller_addr) = get_caller_address()
    # Does not raise error
    assert caller_addr = 123

    %{ stop_prank_callable() %}
    return ()
end
``` 
#### In integration tests
```cairo title="./pranked_contract.cairo"
%lang starknet

from starkware.starknet.common.syscalls import (get_caller_address)

@external
func assert_pranked{syscall_ptr : felt*}():
    let (caller_addr) = get_caller_address()
    with_attr error_message("Not pranked!"):
        assert caller_addr = 123
    end
    return ()
end
```
```cairo title="Remote assert passes"
@contract_interface
namespace Pranked:
    func assert_pranked() -> ():
    end
end

@external
func test_remote_prank{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals
    local contract_address : felt
    %{ 
        ids.contract_address = deploy_contract("./pranked_contract.cairo").contract_address 
        stop_prank_callable = start_prank(123, target_contract_address=ids.contract_address)
    %}
    # Does not raise error
    Pranked.assert_pranked(contract_address=contract_address)
    %{ stop_prank_callable() %}
    return ()
end
``` 


### `roll`

```python
def roll(blk_number: int, target_contract_address: Optional[int] = None) -> Callable[[], None]: ...
```

Changes a block number until the returned function is called. If `target_contract_address` is specified, `roll` affects only the contract with the specified address. Otherwise, `roll` affects the current contract.

```cairo title="Roll cheatcode changes the value returned by get_block_number"
%lang starknet
from starkware.starknet.common.syscalls import get_block_number

@external
func test_changing_block_number{syscall_ptr : felt*}():
    %{ stop_roll = roll(123) %}
    let (bn) = get_block_number()
    assert bn = 123
    %{ stop_roll() %}

    let (bn2) = get_block_number()
    %{ ids.bn2 != 123 %}

    return ()
end
```

### `warp`

```python
def warp(blk_timestamp: int, target_contract_address: Optional[int] = None) -> Callable[[], None]: ...
```

Changes a block timestamp until the returned function is called. If `target_contract_address` is specified, `warp` affects only the contract with the specified address. Otherwise, `warp` affects the current contract.

```cairo title="Warp cheatcode changes the value returned by get_block_timestamp"
%lang starknet

from starkware.starknet.common.syscalls import get_block_timestamp

@external
func test_changing_timestamp{syscall_ptr : felt*}():
    %{ stop_warp = warp(321) %}
    let (bt) = get_block_timestamp()
    assert bt = 321

    %{ stop_warp() %}
    let (bt2) = get_block_timestamp()
    %{ assert ids.bt2 != 321 %}
    return ()
end
```

### `store`
```python
def store(target_contract_address: int, variable_name: str, value: List[int], key: Optional[List[int]] = None):
```
Updates storage variable with name `variable_name` and given key to `value` of a contract with `target_contract_address`.
Example:

```cairo title="./src/contract.cairo"
%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.starknet.common.syscalls import get_block_number

struct Value:
    member a : felt
    member b : felt
end

@storage_var
func store_val(a: felt, b: felt) -> (res: Value):
end

@view
func get_value{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(a: felt, b: felt) -> (
        res : Value):
    let (val) = store_val.read(a, b)
    return (val)
end


```

```cairo title="./test/test_store.cairo"
%lang starknet
from starkware.cairo.common.cairo_builtins import HashBuiltin
from src.contract import Value


@contract_interface
namespace Contract:
    func get_value(a: felt, b: felt) -> (res : Value):
    end
end

@external
func test_store{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():
    alloc_locals
    local contract_address

    %{
        ids.contract_address = deploy_contract("./src/contract.cairo").contract_address
        store(ids.contract_address, "store_val", [4, 3], key=[1,2])
    %}

    let (bn) = Contract.get_value(contract_address, 1, 2)

    assert 4 = bn.a
    assert 3 = bn.b
    return ()
end

```

:::warning
You have to provide `value` and `key` as list of ints. In the future Data Transformer will be supported.
:::

:::warning
There is no type checking for `variable_name`, `value`, `key`, make sure you provided values correctly. 
:::

:::tip
`key` is a list of arguments because cairo `@storage_var` maps any number of felt arguments to any number of felt values
:::

### `load`
```python
def load(target_contract_address: int, variable_name: str, variable_type: List[int], key: Optional[List[int]] = None) -> List[int]:
```
Loads storage variable with name `variable_name` and given `key` and `variable_type` from a contract with `target_contract_address`.
`variable_type` is provided as a string representation of type name.
Example:

```cairo title="./src/contract.cairo"
%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin

struct Value:
    member a : felt
    member b : felt
end

@storage_var
func store_val(a: felt, b: felt) -> (res: Value):
end

@storage_var
func store_felt() -> (res: felt):
end
```

```cairo title="./test/test_store.cairo"
%lang starknet
from starkware.cairo.common.cairo_builtins import HashBuiltin


@external
func test_store{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():
    alloc_locals
    local contract_address
    %{
        ids.contract_address = deploy_contract("./src/contract.cairo").contract_address
        felt_val = load(ids.contract_address, "store_felt", "felt")
        assert felt_val == [0]

        value_val = load(ids.contract_address, "store_val", "Value", key=[1,2])
        assert value_val == [0, 0]
    %}
    return ()
end

```

:::warning
You have to provide `key` as list of ints. In the future Data Transformer will be supported.
:::

:::warning
There is no type checking for `variable_name`, `key`, `variable_type` make sure you provided values correctly. 
:::

:::tip
`key` is a list of arguments because cairo `@storage_var` maps any number of felt arguments to any number of felt values
:::

## Data Transformer
### What is a Data Transformer
Data Transformer converts inputs and outputs of Cairo functions to Python friendly representation. Cairo internally operates on a list of integers, which readability and maintenance becomes problematic for complex data structures. You can read more about: 
- [Data Transformer in the Starknet.py's documentation](https://starknetpy.readthedocs.io/en/latest/guide.html?highlight=Data%20transformer#data-transformation).
- [representing tuples and structs as a list of integers in the official documentation](https://www.cairo-lang.org/docs/hello_starknet/more_features.html#passing-tuples-and-structs-in-calldata)

### Using Data Transformer in cheatcodes
Cheatcodes accept arguments representing input or output of a Cairo function as:
- `List[int]` — a list of integers
- `Dict[DataTransformer.ArgumentName, DataTransformer.SupportedType]` — Data Transformer friendly dictionary

### Example
The following example demonstrate usage on the [`deploy_contract`](#deploy_contract).

```cairo title="./src/main.cairo"
%lang starknet
from starkware.cairo.common.uint256 import Uint256

@constructor
func constructor(initial_balance : Uint256, contract_id : felt):
    # ...
    return ()
end
```


```python title="Passing constructor data as a dictionary"
deploy_contract("./src/main.cairo", { "initial_balance": 42, "contract_id": 123 })
```

```python title="Passing constructor data as a list of integers"
deploy_contract("./src/main.cairo", [42, 0, 123])
```

