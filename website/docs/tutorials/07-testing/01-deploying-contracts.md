---
sidebar_label: Deploying contracts from tests
---

# Deploying contracts from tests

For most projects, testing of isolated functions won't be enough.
Protostar provides a [`deploy_contract` cheatcode](02-cheatcodes/deploy-contract.md) to test interactions between contracts.
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
Please refer to ["passing tuples and structs in calldata"](https://www.cairo-lang.org/docs/hello_starknet/more_features.html#passing-tuples-and-structs-in-calldata) on how to serialize your constructor arguments to array of integers
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
