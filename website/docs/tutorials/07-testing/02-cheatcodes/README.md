# Cheatcodes

Most of the time, testing smart contracts with assertions only is not enough.
Some test cases require manipulating the state of the blockchain, as well as checking for reverts and events.
For that reason, Protostar provides a set of cheatcodes.

Cheatcodes are available inside of [Cairo hints](https://www.cairo-lang.org/docs/hello_cairo/program_input.html#hints).
You don't have to import anything.
When Protostar runs tests, it replaces some core elements in [cairo-lang](https://pypi.org/project/cairo-lang/) library and inject cheatcodes to the hint scope.

:::note
If you are familiar with [Foundry](https://book.getfoundry.sh/forge/cheatcodes.html), you will recognize most cheatcodes.
:::

## Available cheatcodes

```mdx-code-block
import DocCardList from '@theme/DocCardList';
import {useCurrentSidebarCategory} from '@docusaurus/theme-common';

<DocCardList items={useCurrentSidebarCategory().items}/>
```

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
The following example demonstrate usage on the [`deploy_contract`](deploy-contract.md).

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
