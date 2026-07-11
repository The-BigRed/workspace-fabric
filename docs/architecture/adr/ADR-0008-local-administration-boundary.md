# ADR-0008: Local Administration Boundary

## Status

Accepted

## Context

Workspace Fabric exposes a versioned public API intended to serve as the
canonical interface for automation, user interfaces, and third-party
integrations.

Examples include:

- Reference Web UI
- Public CLI
- Home Assistant
- OpenClaw
- Custom automation
- AI agents
- Future third-party clients

These consumers should authenticate using API keys and operate only within the
authorization scopes granted to those keys.

However, a newly installed Workspace Fabric instance presents a bootstrap
problem.

The system intentionally ships without any preconfigured API keys. Until an API
key exists, no authenticated API client—including the Reference Web UI—can
communicate with the controller.

Workspace Fabric also requires a recovery mechanism when administrative
credentials are lost or revoked.

Attempting to solve either problem by introducing authentication bypasses into
the public API would weaken the security model and complicate the
implementation.

Instead, the project recognizes that local operating-system access already
represents administrative ownership of the installation.

## Decision

Workspace Fabric establishes two independent command-line interfaces with
distinct responsibilities.

### Administrative CLI

The Administrative CLI is a trusted local management interface.

It invokes internal application services directly and is intended only for:

- Initial installation
- Bootstrap
- Recovery
- Diagnostics
- Administrative maintenance

Typical operations include:

- Generate the initial API key
- Create additional API keys
- Revoke API keys
- Rotate API keys
- Validate configuration
- Display version information
- Report service health
- Collect diagnostics
- Perform recovery operations

The Administrative CLI is available only to operators with local operating
system access to the Workspace Fabric installation.

It is **not** intended for routine workspace operation.

### Public CLI

The Public CLI is a client of the versioned public API.

It authenticates using API keys and is subject to the same authorization model
as every other API consumer.

The Public CLI exists to perform normal Workspace Fabric operations including:

- Query status
- Apply workspaces
- Apply scenes
- Apply patches
- Execute routes
- Inspect configuration

The Public CLI receives no privileged access beyond the permissions granted to
its API key.

## Bootstrap Workflow

A newly installed Workspace Fabric instance follows this sequence:

```text
Workspace Fabric Installed
            │
            ▼
No API Keys Present
            │
            ▼
Administrative CLI
            │
            ▼
Generate Initial API Key
            │
            ▼
Public API Available
            │
            ▼
Reference Web UI
Public CLI
Automation
Third-party Clients
```

Workspace Fabric intentionally ships without any default credentials.

The installer or administrator creates the first API key through the
Administrative CLI.

## Security Boundary

The operating system provides the administrative trust boundary.

Workspace Fabric does not attempt to authenticate users who already possess
local administrative access to the host.

Instead, the Administrative CLI assumes that operating-system security has
already established ownership of the installation.

Network-based consumers must always authenticate through the public API.

No network request may invoke Administrative CLI functionality.

## Rationale

This design provides several benefits.

### Clean Security Model

The public API has a single authentication model.

There are no special cases for:

- Localhost
- Loopback interfaces
- Local network addresses
- Trusted clients

Every API request authenticates using the same mechanism.

### Secure Bootstrap

The first API key can be created without embedding default credentials in the
product.

The Reference Web UI remains optional and does not participate in the bootstrap
process.

### Recovery

Administrative access remains possible even if all API keys have been revoked,
lost, or corrupted.

Recovery requires local operating-system access rather than undocumented API
behavior.

### API Consistency

Every network client uses the same versioned public API.

Examples include:

- Public CLI
- Reference Web UI
- Home Assistant
- OpenClaw
- AI agents
- Future third-party software

No client receives privileged behavior because of its implementation.

## Consequences

- Workspace Fabric ships without preconfigured API keys.
- The first API key is created locally using the Administrative CLI.
- The Reference Web UI cannot operate until an API key exists.
- The Public CLI authenticates using API keys like every other API client.
- Administrative functionality is intentionally separate from routine
  operational commands.
- The public API contains no authentication bypass for local execution.
- Local operating-system security remains the authoritative administrative
  boundary.

## Alternatives Considered

### API Localhost Bypass

Rejected.

Introducing special authentication behavior for localhost or loopback requests
creates unnecessary complexity and expands the attack surface of the public API.

### Embedded Default Credentials

Rejected.

Shipping default administrative credentials increases deployment risk and
creates additional operational requirements for first-time setup.

### Administrative Operations Through the Public API Only

Rejected.

If all API credentials are lost, no supported recovery path would remain.

A trusted local administrative interface provides a simpler and more reliable
bootstrap and recovery experience.

## Guiding Principle

Workspace Fabric distinguishes between **local administrative ownership** and
**network API authorization**.

Local operating-system access establishes administrative ownership of the
installation.

All network communication—including the Public CLI, Reference Web UI, and
third-party integrations—must authenticate through the versioned public API
using API keys and authorization scopes.

This separation preserves a simple security model while providing robust
installation, bootstrap, and recovery workflows.
