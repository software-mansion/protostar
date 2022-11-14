## Interacting with StarkNet

Protostar provides a couple of commands allowing users to interact with StarkNet without the need to
install [`cairo-lang`](https://pypi.org/project/cairo-lang/) Python package locally.

Protostar offers similar CLI to [StarkNet's CLI](https://docs.starknet.io/docs/CLI/commands). 
However, with Protostar you can move deployment configuration to [`protostar.toml`](/docs/tutorials/project-initialization#protostartoml) and display help for each command.

```mdx-code-block
import DocCardList from '@theme/DocCardList';
import {useCurrentSidebarCategory} from '@docusaurus/theme-common';

<DocCardList items={useCurrentSidebarCategory().items}/>
```

## Using [configuration profiles](../03-project-initialization.md#configuration-profiles)
Configuration profiles allow you to easily reuse configuration for devnet, testnet, and mainnet networks. You can define a network configuration in the `protostar.toml` as demonstrated in the snippet below.

```toml title=protostar.toml
# ...

# https://github.com/Shard-Labs/starknet-devnet
["profile.devnet.protostar.deploy"]
gateway-url="http://127.0.0.1:5050/"

["profile.testnet.protostar.deploy"]
network="testnet"

["profile.mainnet.protostar.deploy"]
network="mainnet"
```

Then, run `deploy` command with the `--profile` argument.
```text
protostar -p devnet deploy ./build/main.json
```
