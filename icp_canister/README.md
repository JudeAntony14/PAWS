Still working on it. ICP has not yet been developed much. This will be the next milestone.

# ICP Canister: Logger

## Deploying the Canister

1. Install [DFINITY SDK (dfx)](https://internetcomputer.org/docs/current/developer-docs/setup/install/).
2. In this `icp_canister/` directory, create a `dfx.json` with the following minimal content:

```json
{
  "canisters": {
    "logger": {
      "main": "logger.mo",
      "type": "motoko"
    }
  }
}
```

3. Deploy locally:

```bash
# Start the local replica (in a new terminal)
dfx start --background
# Deploy the canister
dfx deploy
```

4. Interact with the canister:

```bash
dfx canister call logger record '("Hello ICP!")'
dfx canister query logger view
```

## Python Integration

- Use [`ic-agent-py`](https://github.com/rocklabs-io/ic-py) to call the canister from Python.
- Example usage is provided in the main project README and in the backend Python code. 