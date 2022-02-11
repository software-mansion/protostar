# Protostar 🌟
Toolchain for developing, testing and interacting with Cairo contracts for StarkNet
## Installation
To install the tool run:

```shell
  curl -L https://raw.githubusercontent.com/software-mansion/protostar/master/install.sh | bash
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
    
