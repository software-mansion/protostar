# Cheatcodes

Most of the time, testing smart contracts with assertions only is not enough. Some test cases require manipulating the
state of the blockchain, as well as checking for reverts and events. For that reason, Protostar provides a set of
cheatcodes.

Cheatcodes are available as normal cairo functions. You don't have to import anything. When Protostar runs tests,
it takes care of replacing this functions with code necessary to modify the state of the network.

## Available cheatcodes

```mdx-code-block
import DocCardList from '@theme/DocCardList';
import {useCurrentSidebarCategory} from '@docusaurus/theme-common';

<DocCardList items={useCurrentSidebarCategory().items}/>
```