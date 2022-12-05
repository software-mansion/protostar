# Multicall

## Overview
Multicall allows executing multiple calls while providing [atomicity](https://en.wikipedia.org/wiki/Atomicity_(database_systems)). If one call fails, whole operation fails. Use it to prevent leaving your system in a inconsistent state. 


## Usage example

Before you run [protostar multicall](/docs/cli-reference#multicall), you need to [create an account](./05-deploy-account.md) in order to [sign the transaction](./06-signing.md). If you want to deploy contract within a multicall, you need [declare](./03-declare.md) it first.


Then, create a toml file containing call [array of tables](https://toml.io/en/v1.0.0#array-of-tables).

```toml
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

Protostar supports two types of calls — `deploy` and `invoke`, which accept similar arguments to [`deploy command`](/docs/cli-reference#deploy) and [`invoke command`](/docs/cli-reference#invoke).