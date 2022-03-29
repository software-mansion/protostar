---
sidebar_label: Dependencies (2 min)
---

# Dependencies

Protostar manages dependencies (packages) using [git submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules) ([similarly to Foundry](https://onbjerg.github.io/foundry-book/projects/dependencies.html)). This is the reason Protostar expects [git](https://git-scm.com/) to be installed. Keep this in mind, especially if your project uses git submodules.

:::note
Using Git submodules as a foundation for package management is not an ideal approach. Therefore, [Starkware](https://starkware.co/) plans to create a proper package manager.
:::

## Adding a dependency

To add a dependency, run `protostar install` from the [working directory](https://en.wikipedia.org/wiki/Working_directory) of your project:

```console
$ protostar install https://github.com/bellissimogiorno/cairo-integer-types
12:00:00 [INFO] Installing cairo_integer_types (https://github.com/bellissimogiorno/cairo-integer-types)
```
`lib` folder should now contain the installed dependency:
```console
$ tree -L 2
.
├── lib
│   └── cairo_integer_types
├── protostar.toml
├── src
│   └── main.cairo
└── tests
    └── test_main.cairo
```

### External Dependency Reference Formats

Protostar supports the following ways of referencing external dependency:

| Format                                | Example                                           |
| ------------------------------------- | ------------------------------------------------- |
| `GITHUB_ACCOUNT_NAME/REPO_NAME[@TAG]` | `OpenZeppelin/cairo-contracts@0.1.0`              |
| `URL_TO_THE_REPOSITORY`               | `https://github.com/OpenZeppelin/cairo-contracts` |
| `SSH_URI`                             | `git@github.com:OpenZeppelin/cairo-contracts.git` |


### Aliases

Protostar supports installing dependencies under a different name. This allows you to resolve a name conflict, in case of two GitHub users use the same name for their library. In order to install a package under a custom name, run `protostar install EXTERNAL_DEPENDENCY_REFERENCE --name CUSTOM_NAME`.

## Updating dependencies

To update:
- all dependencies, run `protostar update`
- a single dependency, run `protostar update LOCAL_DEPENDENCY_REFERENCE`

:::info
**LOCAL_DEPENDENCY_REFERENCE** is any reference shown in [External Dependency Reference Formats](#external-dependency-reference-formats) or the name of a directory storing that dependency.
:::


Protostar updates dependencies in the following ways:
- updating to recent tag, if dependency's repository uses [tags](https://git-scm.com/book/en/v2/Git-Basics-Tagging)
- updating to recent commit, if dependency's repository doesn't use tags

## Removing dependencies

To remove a dependency, run `protostar remove LOCAL_DEPENDENCY_REFERENCE`.

