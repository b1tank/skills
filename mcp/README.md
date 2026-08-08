# MCP configuration

`servers.json` is the secret-free canonical MCP manifest used by `setup.sh`.
The bootstrapper projects compatible entries into supported clients while preserving unrelated local configuration.

Credentials are never stored in this repository. Set the environment variables reported by:

```bash
./setup.sh credentials
```

Local product integrations such as Deskpal and OTelux are optional and require those repositories to be installed at the paths shown in `servers.json`.
