# Protostar Website

https://docs.swmansion.com/protostar/

This website is built using [Docusaurus 2](https://docusaurus.io/), a modern static website generator.

## Development

### Requirements

- [Node.js](https://nodejs.org/en/) version >= 14 or above (which can be checked by running `node -v`). You can use nvm for managing multiple Node versions on a single machine installed.

### Running website locally

1. Install yarn: `npm i yarn -g`
2. Install website dependencies: `yarn install`
3. Run the website locally: `yarn start`

## Updating documentation

You can find documentation source files in the `docs` directory. The documentation is written in the `markdown` format. Docusaurus converts markdown files into website.

To change the navigation flow, update `docusaurus.config.js`. This file configures Docusaurus.

[Docusaurus configuration docs](https://docusaurus.io/docs/configuration#what-goes-into-a-docusaurusconfigjs)

## Deployment

Deployment is automatized. When a pull-request is merged to the `master` branch, `../.github/workflows/deploy_docs.yml` builds project and deploys it to the `gh-pages` branch.
