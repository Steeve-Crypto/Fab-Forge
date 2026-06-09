# Grok CLI Reference

## Core Architecture
The CLI uses Click (Python) or Boost.ProgramOptions (C++) for argument parsing, with bindings between components.

## Extensibility
Add new commands via plugins for custom Terafab process modules.

## Examples
- Batch mode for regression testing: `grok-fab batch --file scenarios.yaml`
- Integration with external MES systems via API endpoints.

This CLI demonstrates production-grade tooling skills essential for Terafab.