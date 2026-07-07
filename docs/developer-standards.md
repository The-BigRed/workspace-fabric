# Workspace Fabric Developer Standards

## Purpose

These standards define engineering expectations for both human contributors and AI-assisted development.

## Architectural Standards

- Keep the core hardware agnostic.
- Place vendor-specific logic only in drivers.
- Respect the Resource, Capability, Transaction, and Configuration models.
- Preserve separation between planning and execution.

## Coding Standards

- Prefer readability over cleverness.
- Keep classes and functions focused.
- Return structured errors.
- Avoid hidden global state.

## Testing

Every core feature should include unit tests for success, validation failures, and edge cases. Use mock drivers whenever practical.

## Logging

Logs should explain:
- What was requested.
- What was planned.
- What was executed.
- What actually happened.

## Documentation

Update documentation whenever architecture changes. Significant architectural decisions should become ADRs.

## AI Guidance

AI-generated code should:
- Follow the documented architecture.
- Avoid introducing speculative features.
- Keep pull requests focused.
- Include tests when appropriate.
- Ask for clarification rather than inventing architecture.
