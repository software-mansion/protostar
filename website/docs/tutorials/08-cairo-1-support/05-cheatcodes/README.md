# Cheatcodes

Some tests require specific setup beyond what is possible using standard flow. Protostar exposes
additional functions called cheatcodes that let you do modify the state beyond what is normally possible.

Cheatcodes do not require any specific imports or `use` declarations.

## Error handling in cheatcodes

All cheatcodes return a `Result` enum:

```cairo title="Result"
enum Result<T, felt252> {
    Ok: T,
    Err: E,
}
```

On successful cheatcode execution, a positive result is returned (`OK`) - its exact type depends on the cheatcode.

Depending on cheatcode the type of `Err` may also vary.

### Failing test on cheatcode error

The simplest handling of `Result` is to `unwrap()` them. It either returns a cheatcode success value or causes the test
to
fail entirely:

```cairo title="Simple handling"
use result::ResultTrait;

let prepared_contract = prepare(class_hash, @calldata).unwrap();
```

### `RevertedTransaction`

Cheatcodes `invoke`, `deploy`, `deploy_contract`, `deploy_contract_cairo0`, `declare` and `call` return an `Err` of
type `RevertedTransaction` in case of failure.

```cairo
struct RevertedTransaction {
    panic_data: Array::<felt252>, 
}
```

It also implements a trait:

```cairo
trait RevertedTransactionTrait {
    fn first(self: @RevertedTransaction) -> felt252;
}
```

An example handling of `RevertedTransaction` may look like this

```cairo title="Match handling"
match invoke(deployed_contract_address, 'panic_with', @panic_data) {
    Result::Ok(x) => assert(false, 'Shouldnt have succeeded'),
    Result::Err(x) => {
        assert(x.first() == 'error', 'first datum doesnt match');
        assert(*x.panic_data.at(1_u32) == 'data', 'second datum doesnt match');
    }
}
```

## Available cheatcodes

```mdx-code-block
import DocCardList from '@theme/DocCardList';
import {useCurrentSidebarCategory} from '@docusaurus/theme-common';

<DocCardList items={useCurrentSidebarCategory().items}/>
```