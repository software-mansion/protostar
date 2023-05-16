---
sidebar_label: Dependencies
---

# Dependencies

 Protostar uses [git submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules) to manage dependencies in your project. In order to manage dependencies with Protostar, you must have git installed on your system and have the git executable added to the `PATH` environment variable. The `PATH` variable is a list of directories that your system searches for executables.

:::note
As a temporary solution, Protostar is using git submodules to manage dependencies. 
We recommend migrating your dependency management to [Scarb](https://github.com/software-mansion/scarb).
:::

## Adding a dependency

To add a dependency to your Protostar project, run the following command from the project directory:
```
protostar install EXTERNAL_DEPENDENCY_REFERENCE
```

For example:

```
protostar install OpenZeppelin/cairo-contracts@vX.Y.Z
```


:::danger
It is strongly discouraged to install the dependencies directly from the main branch, because the branch might be in unreleasable state. It is recommended to always include a tag in the [External Dependency Reference format](#external-dependency-reference-formats).
:::

After running the install command, the dependency will be added by default to the `lib` directory in your project:

```console

.
├── lib
│   └── cairo_contracts
│      └── src
├── protostar.toml
├── src
│   └── main.cairo
└── tests
    └── test_main.cairo
```

:::warning
Protostar will create a git commit after installing a dependency.
:::


If you use a dependency that uses absolute imports, you will need to specify a [`cairo-path`](/docs/cli-reference#--cairo-path-path) to the root directory of that dependency in your project.
It is recommended to specify the `cairo-path` in the configuration file, as this setting can be reused by the [`build-cairo0`](/docs/cli-reference#build-cairo0) and [`test-cairo0`](/docs/cli-reference#test-cairo0) commands.


For example:
```toml title="protostar.toml"
[project]
protostar-version = "X.Y.Z"
cairo-path = ["lib/cairo-contracts/src"]
```

### External dependency reference formats

Protostar supports the following ways of referencing external dependency:

| Format                                | Example                                           |
| ------------------------------------- | ------------------------------------------------- |
| `GITHUB_ACCOUNT_NAME/REPO_NAME[@TAG]` | `OpenZeppelin/cairo-contracts@vX.Y.Z`             |
| `URL_TO_THE_REPOSITORY`               | `https://github.com/OpenZeppelin/cairo-contracts` |
| `SSH_URI`                             | `git@github.com:OpenZeppelin/cairo-contracts.git` |

### Aliases

Protostar allows you to install dependencies under a different name, in case of a name conflict between two GitHub users using the same library name. To install a package under a custom name, use [name](/docs/cli-reference#--name-string) argument:

```
protostar install EXTERNAL_DEPENDENCY_REFERENCE --name CUSTOM_NAME
```

For example:

```
protostar install OpenZeppelin/cairo-contracts@vX.Y.Z --name open_zeppelin
```

## Installing dependencies after cloning a repository

If you `git clone` a Protostar project with dependencies without using the `--recurse-submodules` flag, you will need to install the dependencies using Protostar. Otherwise, your project will not compile and tests will fail. To do this, run `protostar install` in the project directory.

```console
protostar install
```

## Updating dependencies

If the default branch of a dependency's repository uses [tags](https://git-scm.com/book/en/v2/Git-Basics-Tagging), Protostar will update the dependency by pulling a commit marked with the newest tag. If the repository does not use tags, Protostar will pull the most recent commit from the default branch.

To update a single dependency, run:

```
protostar update LOCAL_DEPENDENCY_REFERENCE/EXTERNAL_DEPENDENCY_REFERENCE
```

`LOCAL_DEPENDENCY_REFERENCE` is a directory name of a dependency.

To update all dependencies, run:
```
protostar update
```


## Removing dependencies

To remove a dependency from your Protostar project, use the [`protostar remove`](/docs/cli-reference#remove) command and specify the `LOCAL_DEPENDENCY_REFERENCE` or `EXTERNAL_DEPENDENCY_REFERENCE` of the dependency.

```
protostar remove LOCAL_DEPENDENCY_REFERENCE/EXTERNAL_DEPENDENCY_REFERENCE
```

For example, to remove the cairo_contracts dependency, run:
```
protostar remove `cairo_contracts`
```

This command will remove the dependency and all its associated files from your project. Protostar will also create a git commit due to reliance on git submodules.
