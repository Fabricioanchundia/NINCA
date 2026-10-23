# Ninca

Security scanner for [Model Context Protocol (MCP)](https://modelcontextprotocol.io) servers.

> **Status:** early development, not ready for use yet.

Ninca analyzes MCP servers for security risks (tool poisoning, rug pulls, cross-server shadowing, prompt injection through tool outputs, excessive permissions, classic code vulnerabilities, exposed secrets and vulnerable dependencies) and explains each finding in plain language with remediation advice.

Built in Manta, Ecuador.

## Ethics

Ninca performs static analysis of public source code only. It never attacks running servers, and untrusted code is never executed outside an isolated, network-less sandbox.

## Security

See [SECURITY.md](SECURITY.md).

## License

[Apache-2.0](LICENSE)
