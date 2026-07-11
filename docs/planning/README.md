# Planning Framework

## Purpose

The `planning` directory contains the documents that govern the future
development of Workspace Fabric.

During initial development, the project is organized around numbered phases
leading to the first complete public release. Once that milestone is reached,
development transitions to a release-based model. The planning documents in
this directory define how new work is evaluated, accepted, implemented, and
recorded.

These documents are intended to remain stable throughout the lifetime of the
project.

---

# Planning Philosophy

Workspace Fabric intentionally separates architectural vision from development
commitments.

Not every good idea should become an immediate feature.

Likewise, the architecture should leave room for valuable future capabilities
without requiring the project to implement them before there is demonstrated
need.

This distinction allows the project to remain focused while preserving long-term
architectural flexibility.

---

# Planning Documents

## Roadmap

The roadmap defines the planned work required to reach the next major project
milestone.

Prior to the initial public release, the roadmap consists of the numbered
development phases.

Following Release 1.0, the roadmap describes the currently planned release
objectives rather than long-term aspirations.

The roadmap answers:

> Where is the project going next?

---

## Backlog

The backlog contains work that has been accepted by the project.

Items in the backlog represent commitments.

Acceptance does not imply immediate implementation, but it does indicate that
the project intends to complete the work as development priorities allow.

The backlog answers:

> What work has the project committed to?

---

## Architectural Considerations

The Architectural Considerations document captures ideas, opportunities, and
potential platform evolution that the project intentionally leaves room to
support.

Inclusion in this document does **not** represent a commitment to implement the
capability.

Instead, it records architectural considerations that should be kept in mind
when making design decisions so future expansion remains practical where it
provides clear value.

The document also contains the project's current Future Directions, providing
visibility into areas of potential growth without creating implementation
commitments.

Architectural Considerations answers:

> What capabilities should the architecture remain prepared to support?

---

## Release Strategy

The Release Strategy document defines how Workspace Fabric versions are planned,
released, and maintained.

Topics include:

- Semantic Versioning
- Release cadence
- Documentation expectations
- Branch strategy
- Deprecation policy
- Release readiness

The Release Strategy answers:

> How does the project deliver software?

---

## CHANGELOG

The changelog records completed work.

Unlike the backlog, it is purely historical.

Once functionality has been released, its implementation history belongs in the
changelog rather than remaining in the backlog.

The changelog answers:

> What has already been delivered?

---

# Relationship to ADRs

Architectural Decision Records (ADRs) remain the authoritative source for
architectural decisions.

Planning documents must not redefine architecture.

If implementation of a backlog item requires a material architectural change,
the appropriate ADR shall be created and accepted before implementation begins.

Planning follows architecture—not the other way around.

---

# Lifecycle of an Idea

Ideas progress through the project using the following lifecycle.

```text
Idea
    │
    ▼
Architectural Considerations
    │
    │  Accepted for implementation
    ▼
Backlog
    │
    │  Architectural change required?
    ├───────────────┐
    │ Yes           │ No
    ▼               │
   ADR              │
    │               │
    └──────┬────────┘
           ▼
Implementation
    │
    │  Released
    ▼
CHANGELOG
```

Not every idea progresses through every stage.

Many ideas may remain in Future Directions indefinitely.

---

# Promotion to the Backlog

An item should generally move from Future Directions into the Backlog when one
or more of the following conditions are met:

- The capability satisfies a demonstrated operational need.
- The capability has been requested by users.
- The capability naturally extends existing functionality.
- The capability significantly improves usability or maintainability.
- The capability aligns with the project's current development priorities.

Ideas are not promoted solely because they are technically interesting.

---

# Project Priorities

Workspace Fabric development generally follows these priorities:

1. Architectural correctness
2. Reliability
3. Deterministic behavior
4. Usability
5. New functionality

New features should not compromise architectural integrity or operational
predictability.

---

# Release Transition

Completion of Phase 7 constitutes the first complete public release of
Workspace Fabric.

At that point, development transitions from milestone-driven planning to
release-based planning.

Future work will be tracked through:

- Backlog
- Architectural Considerations
- Release Strategy
- CHANGELOG

rather than additional numbered development phases.

---

# Contributor Guidance

When proposing new functionality:

1. Determine whether the capability requires an architectural decision.
2. If necessary, create or update the appropriate ADR.
3. Add long-term ideas to Architectural Considerations.
4. Promote accepted work from Architectural Considerations into the Backlog.
5. Record completed work in the CHANGELOG.

Following this workflow helps maintain a clear separation between architecture,
planning, implementation, and project history.

---

# Guiding Principle

Workspace Fabric is intentionally conservative in its planning.

The project favors stable architecture over rapid feature growth, and
purposefully distinguishes between ideas, commitments, implementation, and
historical record.

This discipline helps ensure that the project remains maintainable, predictable,
and extensible as it evolves.
