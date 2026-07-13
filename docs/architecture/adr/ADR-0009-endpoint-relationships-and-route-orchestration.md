# ADR-0009: Endpoint Relationships and Route Orchestration

## Status

Accepted

---

## Context

Workspace Fabric orchestrates heterogeneous hardware through a unified resource model rather than exposing vendor-specific switching operations.

Although many supported devices perform some form of routing, they differ significantly in both topology and behavior.

Examples include:

* HDMI matrices supporting one-to-many routing
* USB matrices supporting many USB devices connected to a single host
* Audio DSPs
* Remote console systems
* Operating-system agents
* Future software-defined resources

Early implementations naturally modeled routing as simple point-to-point operations.

Experience with the reference hardware demonstrated that this model is insufficient.

Examples include:

* A single HDMI source may intentionally drive multiple displays.
* A USB device may be required to remain assigned to exactly one host.
* Some controllers support a true disconnected state while others require continuous assignment.
* Some routing operations require supporting actions such as EDID configuration or display scaling before the desired relationship can be achieved.

The project therefore requires an architectural model that separates:

* Physical hardware capabilities
* Logical endpoint relationships
* User intent
* Transaction planning
* Driver implementation

This model must remain generic while allowing future hardware classes to introduce additional domain-specific behavior without requiring changes to the core relationship architecture.

---

## Decision

Workspace Fabric models directed endpoint relationships as first-class concepts.

Drivers expose endpoints, capabilities, and routing constraints through metadata.

The Workspace Fabric core interprets those descriptions to validate requested relationships, reconcile desired state, plan supporting operations, and execute deterministic transactions.

Drivers execute assigned operations.

Drivers do not determine orchestration policy.

---

# Endpoint Relationships

A relationship connects a source endpoint to a destination endpoint.

Conceptually:

```text
Source Endpoint
        │
        ▼
Destination Endpoint
```

Relationships are directional.

Direction is defined by endpoint metadata rather than inferred from controller type.

Relationships are logical descriptions of desired connectivity.

They are independent of the native commands required to implement them.

---

# Relationship Intent

Workspace Fabric distinguishes relationship intent from transaction execution.

Relationship intent describes what the caller wishes to achieve.

Examples include:

* Connect a source to a destination.
* Disconnect an endpoint.
* Add an additional destination.
* Replace an existing destination.
* Reconcile a workspace.

Relationship intent enters the transaction planner.

The planner determines:

* Whether the request is valid.
* Whether supporting actions are required.
* Which existing relationships are affected.
* Which driver operations are necessary.
* Whether execution is possible.

Transactions are the implementation produced by that planning process.

---

# Endpoint Constraints

Drivers expose endpoint constraints through metadata.

Examples include:

* Direction
* Accepted endpoint types
* Minimum incoming relationships
* Maximum incoming relationships
* Minimum outgoing relationships
* Maximum outgoing relationships
* Disconnect support
* Required assignment

Conceptually:

```yaml
cardinality:

  incoming:
    min: 0
    max: 1

  outgoing:
    min: 0
    max: many

supports_disconnect: true
```

Another endpoint may instead report:

```yaml
cardinality:

  outgoing:
    min: 1
    max: 1

supports_disconnect: false
```

These constraints describe hardware behavior.

They do not define orchestration policy.

The Workspace Fabric core interprets these constraints when planning transactions.

---

# Relationship Operations

The conceptual relationship operations are:

* Connect
* Disconnect
* Replace
* Reconcile

These describe intent rather than native hardware commands.

Drivers may implement one or more native operations to satisfy each intent.

Some controllers do not support every operation.

Disconnect support, for example, is determined by driver metadata.

---

# Relationship Modes

Relationship intent may specify how existing relationships should be treated.

## Additive

Additive routing preserves existing compatible relationships whenever doing so
does not violate endpoint constraints.

Conflicting relationships may still be replaced when required by hardware
limitations.

Additive routing is the default behavior for direct route requests.

---

## Exclusive

Exclusive routing establishes the requested relationship while removing
confeting relationships within an explicitly defined reconciliation scope.

Exclusive routing shall always identify the scope being reconciled.

Examples include:

* Source
* Destination
* Relationship group
* Managed scope

Workspace Fabric shall not assign a global interpretation to exclusive routing.

---

## Reconcile

Reconciliation causes the managed scope to match the declared desired state.

Relationships not described within that managed scope are removed when required
to achieve the requested state.

Reconciliation is the normal behavior for workspace and scene activation.

---

# Disconnect and Required Assignment

Workspace Fabric distinguishes between disconnecting a relationship and routing
to an isolation destination.

Some controllers support true disconnection.

Others require continuous assignment.

Examples include:

* HDMI outputs that may remain unrouted.
* USB matrices that require every device port to remain assigned to exactly one
  host port.

When a controller requires assignment, routing to a parking endpoint remains a
valid relationship.

Workspace Fabric shall report that relationship truthfully.

Parking is not considered disconnection.

---

# Managed Scope

Workspaces and scenes reconcile only the resources they manage.

Applying a workspace or scene shall not imply reconciliation of unrelated
resources elsewhere in the fabric.

This distinction preserves predictable behavior while allowing future
multi-user, multi-workspace, and distributed deployments.

Managed scope defines the resources over which reconciliation authority exists.

---

# Relationship Groups

Multiple relationships may participate in a single logical operation.

Examples include:

* One source driving multiple destinations.
* Multiple devices assigned to one logical host.
* Future grouped relationships introduced by additional resource domains.

Relationship groups describe logical intent.

The transaction planner may decompose a relationship group into multiple
controller-specific operations.

The existence of a logical relationship group does not require drivers to expose
bulk routing commands.

---

# Transaction Planning

Relationship intent is transformed into executable transactions through the
Workspace Fabric planner.

Planning includes:

* Endpoint compatibility validation
* Cardinality validation
* Constraint evaluation
* Existing relationship analysis
* Conflict detection
* Supporting action selection
* Driver operation generation
* Execution ordering
* Verification planning

Supporting actions required to satisfy the requested relationship become part of
the same transaction.

The planner owns transaction policy.

Drivers execute assigned operations.

---

# Domain Policy Extensions

The relationship model intentionally remains domain independent.

Specialized resource domains may extend relationship behavior through typed
policy models.

Examples include:

## Video

Examples may include:

* EDID reference selection
* Display scaling
* Format compatibility
* Refresh rate requirements
* HDR behavior

## Audio

Future policy may include:

* Gain reference
* Clock source
* Normalization
* Mixing behavior

Additional domains may define their own policy models as needed.

Workspace Fabric intentionally does not define a generic "master/slave"
relationship.

Different resource domains require different authority models.

Domain-specific policies provide explicit semantics appropriate to the resources
they govern.

---

# Responsibilities

Workspace Fabric intentionally separates orchestration from implementation.

## Drivers

Drivers are responsible for:

* Describing endpoints
* Describing capabilities
* Reporting routing constraints
* Reporting observed state where supported
* Executing assigned operations
* Returning structured results

Drivers do not determine:

* User intent
* Reconciliation policy
* Supporting action selection
* Transaction planning
* Global topology decisions

---

## The Workspace Fabric Core

The core is responsible for:

* Relationship validation
* Endpoint compatibility
* Constraint evaluation
* Relationship reconciliation
* Supporting action selection
* Transaction planning
* Transaction execution
* Verification
* Explanation

The core remains the sole authority responsible for orchestration.

---

# Idempotent Behavior

Reapplying an already satisfied relationship should normally result in a
successful no-op.

Workspace Fabric should avoid unnecessary hardware operations when the desired
relationship and supporting state already exist.

The planner remains responsible for determining whether verification or
supporting operations are still required.

---

# Observed State

Workspace Fabric distinguishes between:

* Desired relationships
* Observed relationships
* Last-known relationships
* Assumed relationships
* Unknown relationships

Drivers shall report observed state truthfully.

When hardware cannot verify a relationship, the driver shall report that
limitation rather than claiming successful verification.

---

# Partial Success

Relationship groups may complete only partially.

Examples include:

* One route succeeds while another fails.
* Supporting capability configuration succeeds but routing fails.
* Routing succeeds but verification is unavailable.

Workspace Fabric records the resulting state truthfully.

Logical grouping does not imply hardware-level atomic execution.

---

## Rationale

Separating endpoint description from orchestration preserves the architectural
boundary between drivers and the Workspace Fabric core.

Drivers describe what hardware supports.

The core determines how those capabilities should be used to satisfy user
intent.

This model allows new controller types to participate in planning without
requiring hardware-specific logic within the orchestration engine.

Domain-specific policy extensions allow specialized hardware behavior to evolve
naturally without complicating the generic relationship model.

---

## Consequences

* Endpoint relationships become first-class architectural concepts.
* Drivers remain responsible only for describing hardware and executing assigned
  operations.
* The Workspace Fabric core owns relationship validation and reconciliation.
* Relationship behavior remains consistent across hardware types.
* Domain-specific capabilities extend routing behavior without redefining the
  core relationship model.
* Existing point-to-point driver actions remain valid implementation primitives.
* Future hardware may introduce additional policy models without requiring
  changes to the core relationship architecture.

---

## Alternatives Considered

### Always Additive Routing

Rejected.

Some workflows require deterministic replacement or reconciliation of existing
relationships.

---

### Always Exclusive Routing

Rejected.

Many hardware platforms intentionally support one-to-many or many-to-one
relationships that should be preserved unless the caller explicitly requests
otherwise.

---

### Generic Master/Slave Relationship Model

Rejected.

Authority semantics differ significantly between resource domains.

Video, audio, operating-system resources, and future controller types require
different policy vocabularies.

Typed domain-specific policy models provide clearer semantics while preserving a
stable generic relationship model.

---

### Drivers Own Relationship Planning

Rejected.

Drivers lack sufficient knowledge of the complete fabric topology and user
intent to perform reconciliation safely.

Planning remains a core orchestration responsibility.

---

## Relationship to Other ADRs

* **ADR-0002** defines the controller and driver boundary.
* **ADR-0005** defines driver metadata and endpoint introspection.
* **ADR-0006** defines driver packaging and discovery.
* **ADR-0007** defines the authentication and authorization boundary.

Together these ADRs establish that drivers describe the capabilities and
constraints of individual controllers while the Workspace Fabric core remains
the authoritative orchestrator responsible for validating, reconciling,
planning, and executing endpoint relationships.
