<div align="center">
  <img src="./readme/protostar-logo--light.svg#gh-light-mode-only" width=300 alt="protostar-logo" />
  <img src="./readme/protostar-logo--dark.svg#gh-dark-mode-only" width=300 alt="protostar-logo" />

  <h4>Starknet smart contract development toolchain</h4>

</div>

---
Protostar helps with writing, deploying, and testing your smart contracts. It is loosely inspired by [Foundry](https://github.com/foundry-rs/foundry).

Protostar is actively developed :hammer: . We release every two weeks. Our [roadmap is public](https://github.com/orgs/software-mansion-labs/projects/3/views/3), see what is coming soon!

Install with
```shell
curl -L https://raw.githubusercontent.com/software-mansion/protostar/master/install.sh | bash
```

[Documentation :page_facing_up:](https://docs.swmansion.com/protostar/)


## Table of contents <!-- omit in toc -->
- [Installation](#installation)
- [Development](#development)
  - [Requirements](#requirements)
  - [Setting up environment](#setting-up-environment)
    - [Bumping cairo bindings version](#bumping-cairo-bindings-version)
      - [Caveats:](#caveats)
    - [Submodules development](#submodules-development)
    - [Git hooks](#git-hooks)
- [Updating website/docs](#updating-websitedocs)
- [Deployment](#deployment)





### Additional resources
- [Testing Starknet contracts made easy with Protostar](https://blog.swmansion.com/testing-starknet-contracts-made-easy-with-protostar-2ecdad3c9133)

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
- basic knowledge of [Cairo and Starknet](https://www.cairo-lang.org/docs/index.html)
- basic knowledge of [mypy](https://mypy.readthedocs.io/en/stable/getting_started.html)


### Setting up environment

1. Install Python version management tool: [pyenv](https://github.com/pyenv/pyenv) or [asdf](https://github.com/asdf-vm/asdf)
1. Install `Python 3.9.14` using the Python version management tool and activate that version
   - To be able to build Protostar, set the following environmental variable before installing Python: `PYTHON_CONFIGURE_OPTS="--enable-shared"`
1. Clone this repository
1. Verify the active Python version: `python -V`
1. [Install Poetry](https://python-poetry.org/docs/#installation) — a dependency manager
1. Create Python virtual environment in the project directory: `poetry env use 3.9`
1. Activate environment: `poetry shell`
1. Upgrade pip: `pip install --upgrade pip`
1. Install project dependencies: `poetry install`
    - MacBook M1/M2: `CFLAGS=-I/opt/homebrew/opt/gmp/include LDFLAGS=-L/opt/homebrew/opt/gmp/lib poetry install`
1. Install bindings for the rust tools used by protostar:
    - [install rust](https://www.rust-lang.org/tools/install)
    - `poetry run poe install_cairo_bindings`
1. Patch the git's config by always allowing file transport: `git config --global protocol.file.allow always` (needed for some tests to pass) 
1. Verify the setup by running tests: `poe test`
1. Build Protostar: `poe build`
    - You can find the newly created binary at `dist/protostar/protostar`

#### Bumping cairo bindings version
To bump cairo bindings version to the latest commit on fork (master branch), run: 

```shell
poetry run poe bump_cairo_bindings
```

After this, you can pull & rebuild your local version of bindings by running:
```shell
poetry run poe install_cairo_bindings
```

##### Caveats:
Remember to have your working tree clean, since it creates a commit on the current branch.

The command will check if the tracking branch is master, so you don't commit/push to master by accident (would be rejected by branch protection).


#### Submodules development 
You can use submodules from a different branch than main. Run commands
```shell
git submodule set-branch --branch <your-branch>
poetry run poe install_cairo_bindings
```
Remember to not push those changes to the repository.

#### Git hooks

Run the following script to enable lint checks and automatic formatting before commit/push.

```shell
./scripts/apply_hooks.sh
```

## Updating website/docs
Please read [website/README.md](./website/README.md).

## Deployment
```
$ poe deploy
Current Protostar version: 0.1.0
Provide the new Protostar version:
```
