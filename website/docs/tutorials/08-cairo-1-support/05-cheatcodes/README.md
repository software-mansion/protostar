# Cheatcodes

Some tests require specific setup beyond what is possible using standard flow. Protostar exposes
additional functions called cheatcodes that let you do modify the state beyond what is normally possible.

Cheatcodes do not require any specific imports or `use` declarations.

## Error handling in cheatcodes

All cheatcodes return an `Result` enum:

```cairo title="Result"
enum Result<T, felt252> {
    Ok: T,
    Err: felt252,
}
```

On successful cheatcode execution, `Ok` is returned - an exact type of `Ok` depends on the cheatcode.

On failure, `Err` is returned,
containing [short string](https://github.com/starkware-libs/cairo/blob/26188d4d3271c327fbbfd09f82c4acc99cb281f5/docs/reference/src/components/cairo/modules/language_constructs/pages/literal-expressions.adoc#short-string-literals)
with encoded error message.

### Failing test on cheatcode error

Simplest handling of `Result` is to `unwrap()` them. It either returns a cheatcode success value or causes the test to
fail entirely:

```cairo title="Simple handling"
use result::ResultTrait;

let prepared_contract = prepare(class_hash, @calldata).unwrap();
```

### Matching errors

`Result` can be used inside `match` statement, to handle both `Ok` and `Err` types.

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