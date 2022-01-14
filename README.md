# exercism-manager

Helper script I use to help use [Exercism](https://exercism.org/). It builds upon the Exercism CLI.

## Features:

- Creates buildable stubs by code generation (C track only)
- Track agnostic CLI for building and testing
- Manage solutions from other users (handy for mentoring)
- Some VSCode integration

## Limitations:

- Linux only
- C, Python and Rust tracks only
- IDE suport for VSCode only

## Usage:

- Check out this project to the same directory as your local Exercism.
- `./manage --help`
- Download a solution: `./manage --track=c --exercise=bob download`
- It's ready to build and test: `./manage --track=c --exercise=bob test`
- Open problem files on VSCode: `./manage --track=c --exercise=bob open`
- Submit: `./manage --track=c --exercise=bob submit`