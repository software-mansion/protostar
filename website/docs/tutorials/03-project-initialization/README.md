---
sidebar_label: Project initialization
---

# Project initialization

To create a new project run:

```console
protostar init your-project-name
```

### Adapting an existing project to the Protostar project
Protostar project must be a git repository and have `protostar.toml` file. You can adapt your project manually or by running `protostar init --existing`.

# Project structure

The result of running `protostar init` is a configuration file `protostar.toml`, example files, and the following 3 directories:

- `src` — A directory for your code.
- `lib` — A default directory for an external dependencies.
- `tests` — A directory storing tests.


## Configuration file

The configuration file is required for every Protostar project. It defines the project root, contains crucial information about the project and it can be used as alternative to CLI arguments.

```mdx-code-block
import DocCardList from '@theme/DocCardList';
import {useCurrentSidebarCategory} from '@docusaurus/theme-common';

<DocCardList items={useCurrentSidebarCategory().items}/>