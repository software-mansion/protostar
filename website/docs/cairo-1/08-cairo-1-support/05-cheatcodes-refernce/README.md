# Cheatcodes reference

Some tests require specific setup beyond what is possible using standard flow. Protostar exposes
additional functions called cheatcodes that let you do modify the state beyond what is normally possible.

Cheatcodes do not require any specific imports or `use` declarations.

## Available cheatcodes

```mdx-code-block
import DocCardList from '@theme/DocCardList';
import {useCurrentSidebarCategory} from '@docusaurus/theme-common';

<DocCardList items={useCurrentSidebarCategory().items}/>
```