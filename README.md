<div align="center">
  <img src="./readme/protostar-logo--dark.svg#gh-light-mode-only" width=200 alt="protostar-logo" />
  <img src="./readme/protostar-logo--light.svg#gh-dark-mode-only" width=200 alt="protostar-logo" />

  <h4>StarkNet smart contract development toolchain</h4>

</div>

---

## Table of contents <!-- omit in toc -->
- [About](#about)
- [Documentation](#documentation)
- [Installation](#installation)
- [Development](#development)
  - [Requirements](#requirements)
  - [Setting up environment](#setting-up-environment)
    - [Git hooks](#git-hooks)
- [Updating website/docs](#updating-websitedocs)



## About
Protostar manages your dependencies, compiles your project, and runs tests.

## Documentation
https://docs.swmansion.com/protostar/

## Installation

To install the tool, run:

```shell
curl -L https://raw.githubusercontent.com/software-mansion/protostar/master/install.sh | bash
```
---

## Development

### Requirements
- good knowledge of [Python](https://www.python.org/)
- good knowledge of [pytest](https://docs.pytest.org/en/7.1.x/)
- basic knowledge of [Cairo and StarkNet](https://www.cairo-lang.org/docs/index.html)
- basic knowledge of [mypy](https://mypy.readthedocs.io/en/stable/introduction.html)


### Setting up environment

1. Install Python version management tool: [pyenv](https://github.com/pyenv/pyenv) or [asdf](https://github.com/asdf-vm/asdf)
2. Install `Python 3.7.12` using the Python version management tool and activate that version
3. Clone this repository
4. Verify the active Python version: `python -V`
5. Create Python virtual environment in the project directory: `python -m venv .venv`
6. Activate environment: `source .venv/bin/activate`
7. Install [Poetry](https://python-poetry.org/) — a dependency manager: `pip install poetry`
8. Install project dependencies: `poetry install`
9. Verify the setup by running tests: `poe test`


#### Git hooks

Run the following snippet to enable lint checks and automatic formatting before commit/push.

```shell
cp pre-push ./.git/hooks/
cp pre-commit ./.git/hooks/
chmod +x ./.git/hooks/pre-commit
chmod +x ./.git/hooks/pre-push
```

## Updating website/docs
Please read [website/README.md](./website/README.md).