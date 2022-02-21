# exercism-manager

Helper script I use to help use [Exercism](https://exercism.org/). It builds upon the Exercism CLI.

This purpose of this project is to aid me in learning development practices. PRs are welcome.

## Features:

- Creates buildable stubs by code generation (C track only)
- Track agnostic CLI for building and testing
- Manage solutions from other users (handy for mentoring)
- Enforce pedantic checks to improve on style and best practices.
- Some VSCode integration

## Limitations:

- Linux only (works in WSL too)
- C, Python and Rust tracks only
- IDE suport for VSCode only

## Usage:

- TODO: Explain bootstrap with miniconda
- Check out this project to the same directory as your local Exercism.
- `./manage --help`
- Download a solution: `./manage --track=c --exercise=bob download`
- It's ready to build and test: `./manage --track=c --exercise=bob test`
- Open problem files on VSCode: `./manage --track=c --exercise=bob code`
- Submit: `./manage --track=c --exercise=bob submit`
