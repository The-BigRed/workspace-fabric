# Safety and Recovery

## Purpose

This procedure covers Milestone 3.6 safety and recovery expectations for
physical hardware runs.

Workspace Fabric V0 does not provide automatic rollback. Physical actions should
therefore be treated as operator-supervised transactions: preview the plan,
apply one intended workspace, inspect the result, and keep enough transaction
output to decide the next safe action if a device is unreachable or reports
unknown state.

## Dry-Run First

Before applying a physical workspace, validate the configuration and dry-run the
same workspace request:

```powershell
workspace-fabric config validate --config examples\physical-local.yaml
workspace-fabric apply --config examples\physical-local.yaml desktop --dry-run
```

Inspect the dry-run output before applying:

- Each action should target the expected driver instance.
- Hardware actions should use controller-local physical ports.
- No hardware driver should depend on workspace, scene, or deployment-specific
  resource names.
- Validation warnings should be understood before continuing.

Apply only after the dry-run plan matches the intended physical change:

```powershell
workspace-fabric apply --config examples\physical-local.yaml desktop
workspace-fabric state --config examples\physical-local.yaml
```

`state` is an inspection command. It must not replay saved hardware actions.

## Timeout Handling

Physical driver configurations should use a bounded `connection.timeout_seconds`
value. Driver actions may also receive an action timeout from the core or a
future interface.

When a timeout occurs:

- The driver should return a structured `timeout` error.
- The transaction should report `failed_apply` or `partial_success`.
- Observed state should be `unknown` unless the driver has a verified last-known
  state to report.
- The operator should not treat an echoed command, delayed banner, or missing
  query response as proof that the hardware changed.

If a timeout happens during a smoke test, do not immediately repeat commands in
a tight loop. Check network or serial connectivity, confirm the device is
responsive, and rerun the dry-run before retrying the apply.

## Connection Failure Handling

When a device cannot be reached, the driver should return a structured
`connection_failed` error and avoid reporting fabricated route state.

Common checks:

- Confirm the configured host, TCP port, or serial port.
- Confirm the device is powered and reachable from the controller host.
- Confirm only one process is using a serial transport.
- Confirm the configured transport matches the device connection path.

If one driver fails while other drivers succeed, the transaction result may be
`partial_success`. Treat that as a non-atomic physical state and inspect the
per-action errors before deciding whether to retry or apply a recovery
workspace.

## Retry Guidance

Route actions are intended to be idempotent: applying the same workspace again
should converge hardware toward the same desired routes. Retry only after:

- The configuration still validates.
- The dry-run plan still matches the desired physical outcome.
- The connection or timeout cause has been addressed or bounded.

For a partial success, prefer retrying the same workspace after resolving the
failed driver. This allows already-successful routes to remain correct while the
failed route converges.

## Rollback Guidance

Automatic rollback is deferred beyond V0. Practical rollback for Phase 3 means
applying another explicit workspace that represents the desired recovery state.

Recommended operator workflow:

1. Save the failed transaction output.
2. Run `workspace-fabric state --config examples\physical-local.yaml`.
3. If observed state is `unknown` or `last_known`, physically verify the device
   before assuming the route.
4. Dry-run the previous known-good workspace or a safe workspace.
5. Apply that recovery workspace only when the dry-run plan is correct.

Do not edit persisted state to simulate rollback. Persisted transaction history
is diagnostic context, not a hardware command queue.

## Diagnostics

Keep the JSON output from failed transactions. It should identify:

- The transaction status.
- The failed driver instance.
- The failed action index and path.
- The structured error category.
- Any observed or last-known state.

Hardware driver parse failures should preserve raw device response text in
diagnostics when practical, especially when a device echoes commands or emits
firmware banners before the actual response.
