
## Getting started

### uv
The project and its dependencies are handled with [`uv` from Astral](https://docs.astral.sh/uv/).
The previous links take you to their docs, which also include installation instructions.

After cloning the repo, run

```shell
uv sync
```

This takes care of creating a virtual environment and installs all dependencies.

### Testing

Use `uv run pytest` to run the full test-suite.

### **NOTE**: Some tests actually send emails.

These tests will not run when using the regular `uv run pytest` command, but must be run using `uv run pytest --runslow`

Also, in order for these tests to work Azure VPN must be active.
