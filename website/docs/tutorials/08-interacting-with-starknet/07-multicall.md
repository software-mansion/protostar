# Multicall

## Overview
Multicall executes multiple calls as a single transaction. If one call fails, the entire operation is aborted. Use it to prevent leaving your system in an inconsistent state. 


## Usage example

Before you run [`protostar multicall`](/docs/cli-reference#multicall), you need to [create an account](./05-deploy-account.md) in order to [sign the transaction](./06-signing.md). If you want to deploy contract within a multicall, you need to [declare](./03-declare.md) it first.


Then, create a toml file containing the multicall [array of tables](https://toml.io/en/v1.0.0#array-of-tables).

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

Protostar supports two types of calls — `deploy` and `invoke`, which take similar arguments to [`deploy command`](/docs/cli-reference#deploy) and [`invoke command`](/docs/cli-reference#invoke).

You can use contract address from a previous call by using references (`$DEPLOY_CALL_ID`). References can be used in `contract-address` and `inputs` attributes as demonstrated in the example above.

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
