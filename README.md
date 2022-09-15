<div align="center">
  <img src="./readme/protostar-logo--dark.svg#gh-light-mode-only" width=200 alt="protostar-logo" />
  <img src="./readme/protostar-logo--light.svg#gh-dark-mode-only" width=200 alt="protostar-logo" />

  <h4>StarkNet smart contract development toolchain</h4>

</div>

---

## Table of contents <!-- omit in toc -->
- [About](#about)
- [Documentation](#documentation)
  - [Additional resources](#additional-resources)
- [Installation](#installation)
- [Development](#development)
  - [Requirements](#requirements)
  - [Setting up environment](#setting-up-environment)
    - [Git hooks](#git-hooks)
- [Updating website/docs](#updating-websitedocs)
- [Deployment](#deployment)



## About
Protostar manages your dependencies, compiles your project, and runs tests.

## Documentation
https://docs.swmansion.com/protostar/

### Additional resources
- [Testing StarkNet contracts made easy with Protostar](https://blog.swmansion.com/testing-starknet-contracts-made-easy-with-protostar-2ecdad3c9133)

## Installation

To install the tool, run:

```shell
curl -L https://raw.githubusercontent.com/software-mansion/protostar/master/install.sh | bash
```

If you want to specify a version, run the following command with the requested version:

```console
curl -L https://raw.githubusercontent.com/software-mansion/protostar/master/install.sh | bash -s -- -v 0.3.2
```

---

## Development

### Requirements
- good knowledge of [Python](https://www.python.org/)
- good knowledge of [pytest](https://docs.pytest.org/en/7.1.x/)
- basic knowledge of [Cairo and StarkNet](https://www.cairo-lang.org/docs/index.html)
- basic knowledge of [mypy](https://mypy.readthedocs.io/en/stable/getting_started.html)


### Setting up environment

1. Install Python version management tool: [pyenv](https://github.com/pyenv/pyenv) or [asdf](https://github.com/asdf-vm/asdf)
1. Install `Python 3.9.13` using the Python version management tool and activate that version
   - To be able to build Protostar, set the following environmental variable before installing Python: `PYTHON_CONFIGURE_OPTS="--enable-shared"`
1. Clone this repository
1. Verify the active Python version: `python -V`
1. Create Python virtual environment in the project directory: `python -m venv .venv`
1. Activate environment: `source .venv/bin/activate`
    - Consider using [direnv](https://direnv.net/) to activate the environment on navigating to the project directory
1. Upgrade pip: `pip install --upgrade pip`
1. [Install Poetry](https://python-poetry.org/docs/#installation) — a dependency manager
1. Install project dependencies: `poetry install`
    - MacBook M1/M2: `CFLAGS=-I/opt/homebrew/opt/gmp/include LDFLAGS=-L/opt/homebrew/opt/gmp/lib poetry install`
1. Verify the setup by running tests: `poe test`


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

## Deployment
```
$ poe deploy
Current Protostar version: 0.1.0
Provide the new Protostar version:
```

The ARM version needs to be uploaded manually after the release:
```
$ poe build_installer
```