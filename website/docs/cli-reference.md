# CLI Reference
## Generic flags
#### `--version` `-v`
Show Protostar and Cairo-lang version.
#### `--no-color`
Disable colors.
## Commands
### `init`
```shell
$ protostar init
```
Create a Protostar project.
#### `--existing`
Adapt current directory to a Protostar project.
### `build`
```shell
$ protostar build
```
Compile contracts.
#### `--cairo-path DIRECTORY[]`
Additional directories to look for sources.
#### `--disable-hint-validation`
Disable validation of hints when building the contracts.
#### `--output PATH=build`
An output directory that will be used to put the compiled contracts in.
### `install`
```shell
$ protostar install https://github.com/OpenZeppelin/cairo-contracts
```
Install a dependency as a git submodule.
#### `external_dependency_reference STRING`
- `GITHUB_ACCOUNT_NAME/REPO_NAME[@TAG]`
    - `OpenZeppelin/cairo-contracts@0.1.0`
- `URL_TO_THE_REPOSITORY`
    - `https://github.com/OpenZeppelin/cairo-contracts`
- `SSH_URI`
    - `git@github.com:OpenZeppelin/cairo-contracts.git`

#### `--name STRING`
A custom package name. Use it to resolve name conflicts.