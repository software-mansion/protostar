# Protostar Shell MVP

## Table of Contents

<!-- TOC -->
* [Protostar Shell MVP](#protostar-shell-mvp)
  * [Table of Contents](#table-of-contents)
  * [Terminology](#terminology)
  * [Context](#context)
  * [Goal](#goal)
  * [Architecture](#architecture)
    * [Communication](#communication)
    * [Shell](#shell)
    * [CLI](#cli)
    * [Configuration Parser](#configuration-parser)
    * [Scarb Metadata Parser](#scarb-metadata-parser)
    * [Backend Runner](#backend-runner)
    * [Changes to Backends](#changes-to-backends)
  * [Scope Limitations](#scope-limitations)
<!-- TOC -->

## Terminology

- Backend - binary providing a part of protostar functionality
- Message - arguments provided to the Backend

## Context

As defined in [Protostar modular architecture](protostar-architecture.md), to accelerate
the development of Protostar and simplify integration with [Scarb](https://github.com/software-mansion/scarb)
the whole application will be partitioned into separate smaller binaries.
A layer above these binaries is required to facilitate both running them and, in the future,
simplify communication between Scarb and Protostar.

## Goal

Create a separate Rust application that will provide these features

- Parsing the inputted commands
- Running Protostar binaries
- Resolve the environment details from `protostar.toml` (`Scarb.toml` + `scarb metadata` in the future)
- Providing the binaries with necessary arguments

## Architecture

### Communication

Protostar Shell will use JSON messages to provide commands and environment details to the Backends.

Detailed schema of the message should be decided in revision of this document or in the separate document.

### Shell

The core part of the Protostar Shell will be a base shell that will be able to execute
any binary and parse any commands provided the required configuration.

### CLI

Translate CLI arguments to the Backend message format based on the configuration provided
to the [Shell](#shell).

Initially CLI will be written by-hand to only support `protostar test` command. Other commands
will be simply passed directly to Protostar.

_In the future, better abstraction over these commands can be created. However, eventually all
CLI handling and calling corresponding backends will be done on Protostar Shell side -
Backends will only accept JSON commands. That may result in CLI having to be written by-hand
for most (or all) commands._

### Configuration Parser

Parse configuration file (`protostar.toml` and, in the future, `Scarb.toml`) and resolve
details required for running Backends such as network configuration, contracts' dependencies, etc.

### Scarb Metadata Parser

Parse the output of `scarb metadata` command and resolve details required for running Backends.

### Backend Runner

Run Backends as separate subprocesses and provide them with necessary Messages.

The Backends will be responsible for generating and displaying required inputs. Specifically,
two-way communication will not be introduced as part of Protostar Shell.

Messages will be provided to Backends as inputs when starting their respective subprocesses.

### Changes to Backends

Protostar Backends will have to provide interface compatible with Shell communication format.

Initially whole Protostar will be treated as single Backend. A CLI interface for test-runner
will be created, which will be utilized by Protostar Shell. Other commands will initially
be handled on Protostar side.

## Scope Limitations

Details of Scarb<->Protostar communication were not considered in this document. Initial scope
should be limited to modularizing Protostar and only if possible providing some limited
integration with Scarb. Details of this integrations should be explored in separate document.
