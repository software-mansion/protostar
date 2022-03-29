---
sidebar_label: Dependencies (2 min)
---

# Dependencies

Protostar manages dependencies (packages) using [git submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules) ([similarly to Foundry](https://onbjerg.github.io/foundry-book/projects/dependencies.html)). This is the reason why Protostar expects [git](https://git-scm.com/) to be installed. Keep this in mind, especially if your project uses git submodules.

:::note
Using Git submodules for package management is not ideal approach. Therefore, [Starkware](https://starkware.co/) plans to create proper package manager.
:::

## Adding a dependency

To add a dependency, run `protostar install` from working directory of your project:

```console
$ protostar install https://github.com/bellissimogiorno/cairo-integer-types
12:00:00 [INFO] Installing cairo_integer_types (https://github.com/bellissimogiorno/cairo-integer-types)
```
Folder `lib` should now contain installed dependency:
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

Protostar supports following ways of referencing external dependency:

| Format                                | Example                                           |
| ------------------------------------- | ------------------------------------------------- |
| `GITHUB_ACCOUNT_NAME/REPO_NAME[@TAG]` | `OpenZeppelin/cairo-contracts@0.1.0`              |
| `URL_TO_THE_REPOSITORY`               | `https://github.com/OpenZeppelin/cairo-contracts` |
| `SSH_URI`                             | `git@github.com:OpenZeppelin/cairo-contracts.git` |


### Aliases

Protostar supports installing dependencies with different name. This is allows you to resolve name conflict, in case of two GitHub users use the same name for theirs library. In order to install package with custom name, run `protostar install EXTERNAL_DEPENDENCY_REFERENCE --name CUSTOM_NAME`.

## Updating dependencies

To update:
- all dependencies, run `protostar update`
- a single dependency, run `protostar update LOCAL_DEPENDENCY_REFERENCE`

:::info
**LOCAL_DEPENDENCY_REFERENCE** is any reference shown in [External Dependency Reference Formats](#external-dependency-reference-formats) and the name of a directory storing that dependency.
:::


Protostar updates dependencies in the following ways:
- updating to recent tag, if dependency's repository uses [tags](https://git-scm.com/book/en/v2/Git-Basics-Tagging)
- updating to recent commit, it dependency's repository doesn't use tags

## Removing dependencies

To remove a dependency, run `protostar remove LOCAL_DEPENDENCY_REFERENCE`.

