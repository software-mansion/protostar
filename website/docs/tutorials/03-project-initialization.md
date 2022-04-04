---
sidebar_label: Project initialization (1 min)
---

# Project initialization

To create a new project run:

```console
protostar init
```

```console title="Protostar asks about project name and few other optional information."
Project name: hello-protostar
Project description: 
Author: 
Version: 
License: 
Libraries directory name (optional): 
```

# Project structure
The result of running `protostar init` is a configuration file `protostar.toml`, example files, and the following 3 directories:
- `src` — A directory for your code.
- `lib` — A default directory for an external dependencies.
- `tests` — A directory storing tests.


## `protostar.toml`
```toml
["protostar.general"]
libs_path = "./lib"         # a path to the dependency directory

["protostar.contracts"]
main = [                    # list of cairo contracts
    "src/main.cairo",
]
```