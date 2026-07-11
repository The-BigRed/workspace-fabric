# ADR-0007: Authentication and Authorization Boundary

## Status

Accepted

## Context

Workspace Fabric is a local-first control plane responsible for validating,
planning, and executing deterministic workspace transactions.

Its primary security boundary is the API. Web, desktop, tablet, automation,
monitoring, reporting, and agentic clients interact with the control plane
through that API.

A user with unrestricted local operating-system or shell access to the
Workspace Fabric host may be able to read configuration, access local state,
invoke internal code, or otherwise bypass API enforcement. Workspace Fabric
must not claim that API authorization protects against an administrator or
other equivalently privileged local user.

The project therefore needs a practical API authentication mechanism and a
simple, stable permission model that supports:

- Multiple independently managed client credentials.
- Least-privilege access for monitoring, automation, and agentic clients.
- Broad access for trusted application services.
- A consistent permission vocabulary across all API clients.
- Future user-facing role-based access control without embedding a complete
  identity or policy platform in the core.
- Replacement or expansion of the authentication mechanism without changing
  the public authorization vocabulary.

Workspace Fabric also needs stable identifiers for every object exposed through
the API. Those identifiers are necessary for durable references, audit records,
client-side state, and optional granular authorization implemented by a
consuming UI or service.

The architecture must preserve a clear boundary between:

- Authentication, which identifies an API credential.
- Authorization, which determines the broad classes of operations that
  credential may perform.
- Client-side policy, which may impose more granular restrictions before a
  request reaches Workspace Fabric.
- Execution, which validates, plans, records, and applies an authorized request.

## Decision

Workspace Fabric will use API keys as the initial and primary API
authentication mechanism.

Each API key:

- Has a stable, non-secret key identifier.
- Has a generated secret presented only when the key is created.
- Has a human-readable name and optional description.
- Is assigned one or more OAuth-style permission scopes.
- Can be independently revoked and replaced.
- Is treated as a service credential rather than proof of a human identity.

Multiple API keys may exist simultaneously. Operators should create separate
keys for separate trust boundaries and operational purposes rather than sharing
one universal credential among unrelated clients.

Example deployments may include:

- A trusted UI service key with broad or full permissions. The UI may implement
  its own human-user authentication and granular RBAC before using that key.
- A monitoring and reporting key with read-only permissions.
- An automation or agentic key with selected read and apply permissions but no
  configuration or driver-management authority.
- A configuration-management key with configuration and controller-management
  permissions but no unrestricted route override authority.

Workspace Fabric will enforce only the scopes assigned to the presented API
key. It will not implement per-user, per-role, or per-object authorization in
the core.

## OAuth-Style Permission Scopes

Workspace Fabric uses explicit OAuth-style scopes as its stable authorization
vocabulary.

These scopes describe Workspace Fabric operations rather than client types,
user-interface pages, human roles, or vendor-specific hardware commands.

The initial permission vocabulary is:

```text
fabric.read
fabric.admin

workspace.read
workspace.apply
workspace.edit

scene.read
scene.apply
scene.edit

patch.read
patch.apply
patch.edit

route.read
route.apply
route.override

driver.read
driver.manage

configuration.read
configuration.edit
```

Scopes are additive. An API key should hold only the permissions required for
its intended purpose.

## Scope Semantics

### Fabric

- `fabric.read` permits viewing fabric identity, health, state summaries, and
  non-sensitive metadata.
- `fabric.admin` grants broad administrative authority, including API-key
  administration when that capability is implemented.

`fabric.admin` is an administrative superset, but it does not bypass schema
validation, topology validation, capability checks, transaction planning,
driver boundaries, safety controls, or audit recording.

### Workspaces

- `workspace.read` permits listing and viewing workspaces.
- `workspace.apply` permits requesting activation of a workspace.
- `workspace.edit` permits creating, modifying, and deleting workspace
  definitions.

### Scenes

- `scene.read` permits listing and viewing scenes.
- `scene.apply` permits requesting activation of a scene.
- `scene.edit` permits creating, modifying, and deleting scene definitions.

### Patches

- `patch.read` permits listing and viewing reusable patches.
- `patch.apply` permits applying a defined patch.
- `patch.edit` permits creating, modifying, and deleting patch definitions.

### Routes

- `route.read` permits viewing desired, observed, assumed, last-known, and
  unknown route state as available.
- `route.apply` permits applying routes through supported routing workflows.
- `route.override` permits exceptional low-level route operations that bypass
  higher-level workspace, scene, or patch composition when the API explicitly
  supports those operations.

`route.override` is a high-risk permission. It does not bypass physical topology
validation, controller ownership, capability checks, safety rules, transaction
recording, or driver constraints.

### Drivers

- `driver.read` permits viewing installed driver types, controller identity,
  capabilities, health, exposed ports, and non-secret configuration metadata.
- `driver.manage` permits controller onboarding, connectivity validation,
  driver-specific configuration changes, and supported lifecycle operations.

### Configuration

- `configuration.read` permits viewing and exporting the effective
  configuration, subject to secret redaction.
- `configuration.edit` permits importing, creating, modifying, validating, and
  activating configuration.

Permission to edit configuration does not imply permission to retrieve
plaintext secrets. Secret values should remain write-only or externally
referenced where practical.

## Stable Object Identifiers

Every Workspace Fabric object exposed through the public API must have a stable
unique identifier independent of its display name.

This includes, as applicable:

- Fabrics.
- Controllers.
- Resources.
- Workspaces.
- Scenes.
- Patches.
- Routes or persistent route definitions.
- Driver instances and other managed objects exposed through the public API.

The identifier must remain stable when a display name changes. Names are for
humans; identifiers are for references, API exchange, client-side policy,
transaction records, and audit records.

A UUID is the preferred identifier form unless another globally unique and
stable representation is accepted by the object model.

Conceptually:

```yaml
workspace:
  id: 2f8f0e44-17d7-4ea8-956b-fd6e510b6096
  name: Primary Desktop

scene:
  id: 711a668e-a08a-4bb6-a60a-69602ba1c064
  name: Work Mode

controller:
  id: 06b3b613-d43d-4af2-aa22-16fdf25bde65
  name: Main HDMI Matrix
```

Workspace Fabric returns these identifiers through the API and accepts them in
API requests where an object must be referenced.

Stable object identifiers do not create a per-object authorization requirement
inside Workspace Fabric. They provide the durable reference needed by a
consuming UI or service that chooses to implement granular policy.

## Granular RBAC Boundary

Per-object role-based access control is explicitly outside the Workspace Fabric
core authorization model.

Workspace Fabric does not decide whether a particular human user or role may
apply, edit, or view a specific workspace, scene, patch, controller, or other
object.

A UI or other trusted service may use the stable object identifiers returned by
the API to implement policies such as:

```text
Operator1
  workspace.apply -> Workspace A

Operator2
  workspace.apply -> Workspace B

Engineer
  scene.edit -> Scene 42
```

That policy is maintained and enforced by the UI or service before it submits a
request to Workspace Fabric.

The Workspace Fabric core evaluates only whether the presented API key has the
broad scope required for the requested operation.

Conceptually:

```text
Does this API key have workspace.apply?
```

Workspace Fabric does not additionally evaluate:

```text
Does this user have workspace.apply for object 2f8f...?
```

That second decision belongs to the UI or consuming service.

This design intentionally keeps Workspace Fabric's security model simple while
preserving the information needed for a robust RBAC implementation at another
layer.

## Trusted UI Model

A trusted UI service may authenticate human users, maintain roles and grants,
and decide which object identifiers each user may access.

The UI may then call Workspace Fabric using a broad service API key, potentially
one with full permissions.

In that model:

- Workspace Fabric authenticates and authorizes the UI service key.
- The UI authenticates human users.
- The UI enforces human roles and per-object permissions.
- Workspace Fabric exposes stable object IDs and operation scopes so the UI can
  make deterministic policy decisions.
- Workspace Fabric cannot independently verify the UI's human-level decision.

A broad UI service key must not be embedded in an untrusted browser, desktop
client, mobile client, or other environment where an end user can readily
extract it. It belongs in a trusted server-side component or another adequately
protected execution environment.

## API-Key Lifecycle and Storage

API keys are security-sensitive secrets.

The implementation must:

- Generate keys using a cryptographically secure random source.
- Display the complete secret only at creation time.
- Store a one-way verifier or hash rather than the plaintext key whenever
  practical.
- Store and expose a non-secret key identifier for management and audit use.
- Support explicit revocation.
- Support multiple active keys to permit rotation without downtime.
- Avoid writing complete keys to normal logs, transaction records, errors, or
  telemetry.
- Allow keys to be named so operators can identify their intended client and
  purpose.

Expiration may be supported, but it is not required for the initial local-first
implementation. Revocation and replacement are required lifecycle concepts.

## CLI Boundary

The API authorization model protects API operations. It is not a substitute for
operating-system access control.

A CLI that communicates through the API should use an API key and receive no
special privileges.

A local administrative CLI or direct library invocation may be capable of
bypassing the API boundary. Such access is equivalent to trusted local
administrative access and must be protected by host permissions, file
permissions, service-account isolation, and deployment practices.

Documentation must not imply that Workspace Fabric can enforce API permissions
against a user who already controls the host or the service account running the
control plane.

## Authorization Enforcement

Authorization is enforced by the Workspace Fabric API and control plane before
an operation is planned, recorded as an executable transaction, or dispatched
to a driver.

Drivers do not authenticate API keys and do not authorize users or clients.

Drivers receive only validated actions assigned by the transaction engine. They
must not receive reusable API-key secrets.

Authorization failures must fail closed. A denied request:

- Must not invoke a driver.
- Must not apply or partially apply a transaction.
- Must return a structured authentication or authorization error.
- Should identify the missing scope without exposing credential secrets.
- Should be recorded in the security or audit log when appropriate.

Authentication failure and authorization denial must remain distinguishable.

## Audit Requirements

Authorized and denied API operations should record, where available:

- API-key identifier, never the complete secret.
- API-key name or client label.
- Evaluated scope.
- Target object identifier, when the request references an object.
- Requested operation.
- Resulting transaction identifier, if one was created.
- Success, denial, warning, or failure outcome.

When a trusted UI uses a shared service key, Workspace Fabric's authoritative
identity is the UI credential. Any human-user identity supplied by the UI is
informational unless a future trusted delegation mechanism makes it verifiable.

Audit records must not contain passwords, complete API keys, bearer tokens,
private keys, or other reusable credentials.

## Future Authentication Providers

API keys are the v0.3 authentication decision, not a permanent prohibition on
other mechanisms.

Future releases may add OAuth 2.0, OpenID Connect, mutual TLS, or external
identity-provider integrations. Those mechanisms should map authenticated
principals to the same broad scope vocabulary rather than introducing
per-object authorization into the core by default.

Adding another authentication provider requires a separate architectural and
security review. It must not silently broaden the permissions of existing API
keys or change established scope semantics.

## Rationale

API keys are appropriate for the initial local-first product because they are:

- Straightforward to generate, distribute, rotate, and revoke.
- Suitable for service-to-service clients and automation.
- Independent of any external identity service.
- Compatible with a future UI that owns human authentication and RBAC.
- Able to support multiple purpose-specific trust boundaries.

OAuth-style scopes provide a stable permission vocabulary without requiring an
OAuth authorization server.

Stable object identifiers support durable API references, transaction history,
audit records, and optional per-object RBAC implemented by a consuming UI or
service.

Keeping per-object authorization outside the core preserves Workspace Fabric as
a focused control plane rather than turning it into a general-purpose identity
and policy platform.

## Consequences

- API keys are the initial supported API authentication mechanism.
- Multiple keys with different broad scopes are expected and encouraged.
- Scope names and semantics become part of the stable public API contract.
- Existing scope semantics must not be silently broadened in a way that grants
  materially greater authority.
- Every API-visible object requires a stable unique identifier.
- Object display names may change without changing references.
- Workspace Fabric does not store or enforce per-user, per-role, or per-object
  grants.
- Trusted UIs and services may implement granular RBAC using the object IDs
  exposed by the API.
- A shared full-permission UI key places the human authorization boundary in the
  UI and must not be embedded in an untrusted client.
- API authorization does not protect against users with equivalent local
  administrative access to the Workspace Fabric host.
- Drivers remain unaware of API keys, users, roles, and policy decisions.
- Future authentication providers may be added without replacing the broad
  scope model or moving granular RBAC into the core.
