# Scripting
In order to automate a process of your desire that includes protostar operations, you may want to assemble some protostar commands and put them in a single script.

This tutorial shows a simple example of how to do such a thing using scripting in bash.

### File Structure

Let's create the following file structure:

```
- src
  - basic_contract.cairo
- tests
  - test_basic_contract.cairo
- protostar.toml
```

#### Basic contract

```cairo
%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin

@storage_var
func balance() -> (res: felt) {
}

@constructor
func constructor{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    initial_balance: felt
) {
    balance.write(initial_balance);
    return ();
}


@external
func increase_balance{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    amount: felt
) {
    let (res) = balance.read();
    balance.write(res + amount);
    return ();
}

@view
func get_balance{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() -> (res: felt) {
    let (res) = balance.read();
    return (res,);
}
```

#### Test for the contract

```cairo
%lang starknet

from starkware.cairo.common.math import assert_le

@contract_interface
namespace BasicContract {
  func increase_balance(amount: felt) -> () {
  }
  func get_balance() -> (res: felt) {
  }
}

@external
func setup_basic() {
    %{
      context.contract_address = deploy_contract("./src/basic_contract.cairo", [100]).contract_address
    %}
    return ();
}

@external
func test_basic{syscall_ptr: felt*, range_check_ptr}() {
    alloc_locals;

    local contract_address: felt;
    %{ ids.contract_address = context.contract_address %}

    let (res,) = BasicContract.get_balance(contract_address=contract_address);
    assert res = 100;

    BasicContract.increase_balance(contract_address=contract_address, amount=50);
    let (res,) = BasicContract.get_balance(contract_address=contract_address);
    assert res = 150;

    return ();
}
```

#### protostar.toml file

You can read about how to compose the protostar configuration file [here](../04-configuration-file.md). The point is to keep protostar commands clean and simple and leave such things as the network configuration away from them.

### Bash script

Let's assume we want to automate deploying our contract. But before we deploy, we want to first run the tests and check if everything is alright. Instead of manually invoking all the necessary commands, we could write a bash script for that.

#### Setup the script

Let's start with something like this:

```shell
#!/bin/bash

set -e
```

The first line informs the system which interpreter should be used to run the script.

The `set -e` instruction tells the interpreter to exit the script immediately if any command returns a non-zero status. This is good for us because we don't want to run the following instructions if one of them fails, for example, we do not want to deploy a contract if the tests for this contract failed.

#### Make sure the contract is correct

```shell
protostar build
protostar test
```

In order to be able to use this, you have to have protostar installed. You can see how to do this [here](../02-installation.md).

These two instructions assure that the contract builds properly and all tests pass.

#### Declare and deploy the contract

Now, we need to first [declare](./03-declare.md) the contract and then [deploy](./04-deploy.md) it.

Normally, we would start with something like this:

```shell
protostar declare ./build/main.json
```

But `deploy` command needs the contract's class hash that comes from the `declare`'s command output. Therefore we need to get this output in a standardized way. That's when the `--json` flag comes into play.

By doing:

```shell
protostar declare ./build/main.json --json
```

we get an output like this:

```json
{"class_hash":"0x07a70656b5612a2f87bd98af477c0be5fa2113d13fe1069e55ad326a3e6f4fe6","transaction_hash":"0x01f6a2c391d1bd0a51322ba73037ada20e0b30da8232bb86028f813a0d4c1fdb"} 
```

Now, we can parse the json and pull all the desired information from it easily as json is a format that is widely supported.

We could do something like this in our bash script:

```shell
OUTPUT=$(protostar declare ./build/main.json --json)
CLASS_HASH=$(python -c "import sys, json; print(json.loads(sys.argv[1])['class_hash'])" $OUTPUT)
protostar deploy $CLASS_HASH --inputs 100
```

#### Call the contract

Now, let's say we want to call our contract. In this case, we need the contract address that is being returned from the `deploy` command call.

We are basically going to do the same thing as previously to pass the contract address from `deploy` to `call`:

```shell
OUT=$(protostar deploy $CLASS_HASH --inputs 100 --json)
CONTRACT_ADDRESS=$(python -c "import sys, json; print(json.loads(sys.argv[1])['contract_address'])" $OUT)
protostar call --contract-address $CONTRACT_ADDRESS --function get_balance
```

In the end, our bash script looks like this:

```shell
#!/bin/bash

set -e

protostar build
protostar test

DECLARE_OUTPUT=$(protostar declare ./build/main.json --json)
CLASS_HASH=$(python -c "import sys, json; print(json.loads(sys.argv[1])['class_hash'])" $DECLARE_OUTPUT)

DEPLOY_OUTPUT=$(protostar deploy $CLASS_HASH --inputs 100 --json)
CONTRACT_ADDRESS=$(python -c "import sys, json; print(json.loads(sys.argv[1])['contract_address'])" $DEPLOY_OUTPUT)
protostar call --contract-address $CONTRACT_ADDRESS --function get_balance
```

Of course, we could exclude pulling a specific field from the output to a separate bash function but that's not important.

Using `--json` flag is also good if you prefer the more compressed output from protostar commands.
