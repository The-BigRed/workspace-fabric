# Workspace Fabric AI Coding Guidelines

## General Rules

- Keep core logic hardware-agnostic.
- Put vendor-specific behavior only in drivers.
- Prefer explicit models over implicit assumptions.
- Keep functions small and testable.
- Validate before applying changes.
- Return structured errors.
- Write tests for every new core behavior.
- Do not silently ignore invalid configuration.
- Do not invent architecture that contradicts docs.

## Configuration

- YAML is the initial config format.
- Config should be validated before use.
- Missing references should produce clear errors.
- Duplicate IDs should fail validation.
- Do not assume all fabrics or matrices share topology.

## Resource Graph

- Resource attachment is explicit.
- USB host maps are per matrix.
- A USB route is valid only if the owning matrix has the target host attached.
- A display should be modeled by logical identity, not output number.
- Hardware ports are implementation details.

## Drivers

- Use mock drivers first.
- Drivers report capabilities.
- Drivers report state honestly.
- If state cannot be queried, return unknown.
- Do not fake success for unsupported features.
- Drivers should not make global policy decisions.

## Transactions

- Always validate before applying.
- Support dry-run planning.
- Separate planning from execution.
- Record warnings and partial failures.
- Do not require rollback in V0.

## Tests

Minimum tests should cover:

- Valid config.
- Invalid missing references.
- Duplicate IDs.
- Valid USB route.
- Invalid USB route due to missing host attachment.
- Capability `prefer` warning.
- Capability `require` failure.
- Transaction dry run.
- Mock transaction execution.
