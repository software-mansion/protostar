<div style="display: flex; flex: 1; flex-direction: column; align-items: center; border-bottom: 2px solid rgba(128,128,128,0.25); padding-bottom: 1rem; margin-bottom: 2rem;">
<img src="website/static/img/protostar-logo--dark.png" width=80 alt="protostar-logo" />
<h1 style="display: inline-block; border-bottom: none; margin-bottom: 0;"><b>PROTO</b>STAR</h1>
StarkNet smart contract development toolchain
</div>

## Installation

To install the tool run:

```shell
  curl -L https://raw.githubusercontent.com/software-mansion/protostar/master/install.sh | bash
```

## Development

### Tools

- [Poetry](https://python-poetry.org/) - dependency manager
- [pyenv](https://github.com/pyenv/pyenv) - recommended for installing and switching python versions locally

Make sure running `poetry run python --version` returns `Python 3.7.12`.

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
