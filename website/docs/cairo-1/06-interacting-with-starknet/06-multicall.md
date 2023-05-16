# Multicall

## Overview
Multicall executes multiple calls as a single transaction. If one call fails, the entire operation is aborted. Use it to prevent leaving your system in an inconsistent state. 


## Usage example

First, create a toml file containing calls defined as [array of tables](https://toml.io/en/v1.0.0#array-of-tables).
In this file, you can use contract address of a contract to be deployed by using references (`$DEPLOY_CALL_ID`).
References can be used in `contract-address` and `inputs` attributes as demonstrated in the example below.

```toml title="calls.toml"
[[call]]
type = "deploy"
class-hash = 0xDEADBEEF
inputs = []
id = "my_contract"

[[call]]
type = "invoke"
contract-address = "$my_contract"
function = "increase_balance"
inputs = [42]
```


Protostar supports two types of transactions — `deploy` and `invoke`, which take similar arguments to [`deploy` command](/docs/cli-reference#deploy) and [`invoke` command](/docs/cli-reference#invoke).

When choosing `deploy` transaction type, the deployment happens through the Universal Deployer Contract (UDC), see the [`deploy` command](/docs/cli-reference#deploy) for more information.


```toml title="protostar.toml"
[project]
protostar-version = "0.8.1"

[multicall]
account-address = 0x...
gateway-url = "http://127.0.0.1:5050"
chain-id = 1536727068981429685321
max-fee = "auto"
```

```shell title="Calling multicall"
export PROTOSTAR_ACCOUNT_PRIVATE_KEY 0x...
protostar multicall calls.toml
```

```shell title="Protostar shows transaction hash and addresses of deployed contracts"
Multicall has been sent.
transaction hash: 0x...
my_contract     : 0x...
```
