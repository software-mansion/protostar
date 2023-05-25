# Scripting

In order to automate a process that includes protostar operations, you may want to build a script in language of your
choice.

This tutorial shows a simple example of how to do such a thing using scripting in bash.

We are going to write a script that builds, tests, declares, deploys, and, in the end, calls the contract. We are also
going to make use of the protostar's structured output, so we can use previous' commands outputs in the following ones.

### File Structure

First, let's create a basic protostar file structure. You can generate it by
calling [`protostar init`](../03-project-initialization.md). It looks like this:

```
my_project/
├── src/
│   ├── business_logic/
│   │   └── utils.cairo
│   ├── contract/
│   │   └── hello_starknet.cairo
│   ├── business_logic.cairo
│   ├── contract.cairo
│   └── lib.cairo
└── Scarb.toml
├── tests/
│   ├── test_hello_starknet.cairo
│   └── test_utils.cairo
└── protostar.toml
```

#### The contract

`protostar init` automatically fills generated files with sample content. We're not going to change them, because the
example contract is sufficient for us, and it is not important for this tutorial what it does exactly.

#### protostar.toml file

You can read about how to compose the protostar configuration file [here](../05-protostar-toml.md). The point is to keep
protostar commands clean and simple and leave such things as the network configuration away from them.

In this file, you should create the following sections:

- `declare-cairo1`
- `deploy`
- `call`

In these sections, you can specify properties like `network`, `account-address`, or `private-key-path`.

### Bash script

#### Setup the script

Let's start with something like this:

```shell title="automate_protostar_operations.sh"
#!/bin/bash

set -e
```

The first line informs the system which interpreter should be used to run the script.

The `set -e` instruction tells the interpreter to exit the script immediately if any command returns a non-zero status.
This is good for us because we don't want to run the following instructions if one of them fails, for example, we do not
want to deploy a contract if the tests for this contract failed.

#### Make sure the contract is correct

```shell title="automate_protostar_operations.sh"
protostar build
protostar test
```

These two instructions assure that the contract builds properly and all tests pass.

#### Declare and deploy the contract

Now, we need to first [declare](./02-declare.md) the contract and then [deploy](./03-deploy.md) it.

Normally, we would start with something like this:

```shell
protostar declare-cairo1 hello_starknet
```

But the `deploy` command needs the contract's class hash that comes from the `declare-cairo1` command output. Therefore,
we need to get this output in a standardized way. That's when the `--json` flag comes into play.

By doing:

```shell
protostar declare-cairo1 hello_starknet --json
```

we get an output like this:

```json
{
  "class_hash": "0x07a70656b5612a2f87bd98af477c0be5fa2113d13fe1069e55ad326a3e6f4fe6",
  "transaction_hash": "0x01f6a2c391d1bd0a51322ba73037ada20e0b30da8232bb86028f813a0d4c1fdb"
} 
```

:::note
The `--json` output is, in fact, formatted in [NDJSON](https://github.com/ndjson/ndjson-spec), but here we operate on
commands that return a single message, therefore we can treat them as JSONs.
:::

Now, we can parse the json and pull all the desired information from it easily as json is a format that is widely
supported.

We could do something like this in our bash script:

```shell title="automate_protostar_operations.sh"
OUTPUT=$(protostar declare ./build/main.json --json)
CLASS_HASH=$(python -c "import sys, json; print(json.loads(sys.argv[1])['class_hash'])" $OUTPUT)
protostar deploy $CLASS_HASH --inputs 100
```

You can use any alternative to python that will parse the json for you. This is how it would work
with [jq](https://stedolan.github.io/jq/):

``` title="automate_protostar_operations.sh"
OUTPUT=$(protostar declare-cairo1 hello_starknet --json)
CLASS_HASH=$(echo $OUT | jq -r ".class_hash")
protostar deploy $CLASS_HASH --inputs 100
```

#### Call the contract

Now, let's say we want to call our contract. In this case, we need the contract address that is being returned from
the `deploy` command call.

We are basically going to do the same thing as previously to pass the contract address from `deploy` to `call`:

```shell title="automate_protostar_operations.sh"
OUT=$(protostar deploy $CLASS_HASH --inputs 100 --json)
CONTRACT_ADDRESS=$(python -c "import sys, json; print(json.loads(sys.argv[1])['contract_address'])" $OUT)
protostar call --contract-address $CONTRACT_ADDRESS --function get_balance
```

In the end, our bash script looks like this:

```shell title="automate_protostar_operations.sh"
#!/bin/bash

set -e

protostar build
protostar test

DECLARE_OUTPUT=$(protostar declare-cairo1 hello_starknet --json)
CLASS_HASH=$(python -c "import sys, json; print(json.loads(sys.argv[1])['class_hash'])" $DECLARE_OUTPUT)

DEPLOY_OUTPUT=$(protostar deploy $CLASS_HASH --inputs 100 --json)
CONTRACT_ADDRESS=$(python -c "import sys, json; print(json.loads(sys.argv[1])['contract_address'])" $DEPLOY_OUTPUT)
protostar call --contract-address $CONTRACT_ADDRESS --function get_balance
```

Of course, we could exclude pulling a specific field from the output to a separate bash function but that's not
important.

Using the `--json` flag may also be good if you prefer the more compressed output from protostar commands.

### Python script

The main advantage of using the JSON format is that the user may automate protostar operations easily no matter what
languages and technologies they use.

We can achieve the same result as above writing the equivalent python script:

```python title="automate_protostar_operations.py"
import subprocess, json


def run_command(cmd):
    out = subprocess.check_output(cmd.split(" "))
    return out.decode("utf-8")


print("BUILD")
run_command("./protostar build")
print("TEST")
run_command("./protostar test")
print("DECLARE")
out = run_command("./protostar declare-cairo1 hello_starknet --json")
print("DEPLOY")
class_hash = json.loads(out)['class_hash']
out = run_command(f"./protostar deploy {class_hash} --inputs 100 --json")
print("CALL")
contract_address = json.loads(out)['contract_address']
out = run_command(f"./protostar call --contract-address {contract_address} --function get_balance --json")
print(out)

print("DONE")
```
