# Protostar 🌟
Toolchain for developing, testing and interacting with Cairo contracts for StarkNet
## Installation
To install the tool run:

```shell
  curl -L https://raw.githubusercontent.com/software-mansion/protostar/master/install.sh | bash
```
## Commands
```shell
protostar init
```
Interactively creates a new project 

---
```shell
protostar compile main.cairo
```
Builds cairo project from source files

---
```shell
protostar install <package_name>
```
Installs cairo package as git submodule. \
`<package_name>` can be:
- repository http url - ex. `https://github.com/software-mansion/protostar.git`
- repository ssh url - ex. `git@github.com:software-mansion/protostar.git`
- github repository name - ex. `software-mansion/protostar`
You can use `--name` argument to install package using custom name and later reference it using this custom name.

---
```shell
protostar update <package_name>
```
Updates previously installed package \
`<package_name>` can be:
- repository http url 
- repository ssh url
- github repository name \
as long as it points to the same repository as one of already installed packages. \

---
```shell
protostar remove <name>
```
Removes previously installed package \
`<package_name>` can be:
- repository http url 
- repository ssh url
- github repository name \
as long as it points to the same repository as one of already installed packages.

---
```shell
protostar test
```
Runs cairo tests in the project

---
To see any additional flags for a certain command run
```
protostar <command> --help
```
## Development
### Tools

- [Poetry](https://python-poetry.org/) - dependency manager
- [pyenv](https://github.com/pyenv/pyenv) - recommended for installing and switching python versions locally

Make sure running ``poetry run python --version`` returns ``Python 3.7.12``.

### Setup
Make sure you have [Poetry](https://python-poetry.org/) installed before running `install`
```shell
# Install dependencies
poetry install
```

### Git hooks
Run this snippet to enable lint checks and automatic formatting before commit/push.

```shell
cp pre-push ./.git/hooks/
cp pre-commit ./.git/hooks/
chmod +x ./.git/hooks/pre-commit
chmod +x ./.git/hooks/pre-push
```
    
