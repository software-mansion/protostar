---
sidebar_label: Migrations
---

# Migrations

Migrations are Cairo files that help you deploy contracts to the StarkNet network. They are especially useful, when your project consists of multiple contracts. Migration code is mainly written in hints. Protostar injects special functions into hints' scope, which you can use to interact with the StarkNet. These functions are similar to cheatcodes used to test contracts, hence in this document we will refer to these functions as Migration Cheatcodes.

:::info
Protostar aims to make Migration Cheatcodes a subset of Testing Cheatcodes in order to allow testing migration scripts against Protostar's StarkNet. 
:::

## Creating a migration file
You can create a migration file anywhere, but we recommend creating them inside a `migrations` directory. Currently, Protostar doesn't enforce any naming convention for migration files. We recommend name: `migration_NUMBER_TITLE.cairo`, for example `migration_01_init.cairo`.

:::info
You can't import a Cairo file, if its name starts with a digit. In the future, you might import your migration files for testing purposes.
:::

## Migration file structure
Each migration should have 2 functions: `up` and `down`. The `up` function is responsible to migrate your project forward,  and the `down`function is executed to rollback changes.

```python title="'up' and 'down' functions must be decorated with '@external' decorator"
%lang starknet

@external
func up():
    %{ declare("./build/main.json") %}
    return ()
end

@external
func down():
    %{ assert False, "Not implemented" %}
    return ()
end

``` 

## Running the migration
T.B.D.


## Available migration cheatcodes
```mdx-code-block
import DocCardList from '@theme/DocCardList';
import {useCurrentSidebarCategory} from '@docusaurus/theme-common';

<DocCardList items={useCurrentSidebarCategory().items}/>
```
