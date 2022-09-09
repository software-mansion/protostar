---
sidebar_label: Dependencies
---

# Dependencies

Protostar manages dependencies (packages) using [git submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules) ([similarly to Foundry](https://onbjerg.github.io/foundry-book/projects/dependencies.html)). This is the reason Protostar expects [git](https://git-scm.com/) to be installed. Keep this in mind, especially if your project uses git submodules.

:::note
Using Git submodules as a foundation for package management is not an ideal approach. Therefore, [Starkware](https://starkware.co/) plans to create a proper package manager.
:::

## Adding a dependency

To add a dependency, inside project directory, run `protostar install EXTERNAL_DEPENDENCY_REFERENCE`:

```console title="Installing a dependency from link to a repository."
$ protostar install https://github.com/OpenZeppelin/cairo-contracts
12:00:00 [INFO] Installing cairo_contracts (https://github.com/OpenZeppelin/cairo-contracts)
```

```console title="'lib' category contains the installed dependency."
$ tree -L 2
.
├── lib
│   └── cairo_contracts
├── protostar.toml
├── src
│   └── main.cairo
└── tests
    └── test_main.cairo
```

:::warning
Protostar creates a git commit after installing a dependency.
:::

:::warning
If you use a dependency that uses absolute imports, you have to specify a cairo-path to the project's root directory of that dependency. You can do it in the following way:

```cairo title="./lib/cairo_contracts/src/openzeppelin/account/Account.cairo"
// ...

from openzeppelin.introspection.ERC165 import ERC165_supports_interface

// ...
```

```shell
protostar build --cairo-path ./lib/cairo_contracts/src
```
:::

:::info
You can configure your `cairo-path` in [the configuration file](/docs/tutorials/project-initialization#protostartoml).
:::


### External dependency reference formats

Protostar supports the following ways of referencing external dependency:

| Format                                | Example                                           |
|---------------------------------------|---------------------------------------------------|
| `GITHUB_ACCOUNT_NAME/REPO_NAME[@TAG]` | `OpenZeppelin/cairo-contracts@0.1.0`              |
| `URL_TO_THE_REPOSITORY`               | `https://github.com/OpenZeppelin/cairo-contracts` |
| `SSH_URI`                             | `git@github.com:OpenZeppelin/cairo-contracts.git` |

### Aliases

Protostar supports installing dependencies under a different name. This allows you to resolve a name conflict, in case of two GitHub users use the same name for their library. In order to install a package under a custom name, run `protostar install EXTERNAL_DEPENDENCY_REFERENCE --name CUSTOM_NAME`. [Updating dependencies](#updating-dependencies) section explains how to refer to installed dependency.

```console title="Installing a dependency under different name."
$ protostar install https://github.com/OpenZeppelin/cairo-contracts --name open_zeppelin
10:09:51 [INFO] Installing open_zeppelin (https://github.com/OpenZeppelin/cairo-contracts)
```

## Installing dependencies after cloning a repository

If you [clone](https://git-scm.com/docs/git-clone) Protostar project using dependencies without `--recurse-submodules` flag, you need to install dependencies using Protostar. Otherwise, your project won't compile and tests will fail. To do so, run `protostar install` in the project directory.

```console title="Protostar will install all submodules from the dependencies directory."
$ protostar install
09:37:42 [INFO] Installing cairo_contracts (https://github.com/OpenZeppelin/cairo-contracts)
```

## Updating dependencies

To update:

- a single dependency, run `protostar update LOCAL_DEPENDENCY_REFERENCE/EXTERNAL_DEPENDENCY_REFERENCE`
- all dependencies, run `protostar update`

`LOCAL_DEPENDENCY_REFERENCE` is a directory name of a dependency, for example:

```console title="Updating a previously installed dependency."
$ protostar update cairo_contracts
10:03:52 [INFO] Package already up to date.
```

If the default branch of a dependency's repository uses [tags](https://git-scm.com/book/en/v2/Git-Basics-Tagging), Protostar will pull a commit marked with the newest tag. Otherwise, Protostar will pull a recent commit from the default branch.

## Removing dependencies

To remove a dependency, run `protostar remove LOCAL_DEPENDENCY_REFERENCE/EXTERNAL_DEPENDENCY_REFERENCE`.

```console title="Removing a dependency."
$ protostar remove cairo_contracts
10:04:26 [INFO] Removing cairo_contracts
```
