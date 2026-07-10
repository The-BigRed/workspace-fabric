# Physical Smoke Test

## Purpose

This checklist covers the Milestone 3.5 end-to-end physical smoke test for the
Phase 3 lab configuration in `examples/physical-local.yaml`.

The goal is to prove that Workspace Fabric can resolve user-facing workspace
intent into UHD-808 and UKM-404 controller-local port actions, apply those
actions through the configured hardware drivers, and report observed route state
where the hardware query succeeds.

## Scope

Run the smoke test against these workspaces, in order:

1. `desktop`
2. `work`
3. `hybrid_meeting`

This milestone does not add the future scene or patch YAML schema. It applies
the currently implemented V0 workspace model.

## Commands

Validate the physical configuration:

```powershell
workspace-fabric config validate --config examples\physical-local.yaml
```

Dry-run each workspace before applying it:

```powershell
workspace-fabric apply --config examples\physical-local.yaml desktop --dry-run
workspace-fabric apply --config examples\physical-local.yaml work --dry-run
workspace-fabric apply --config examples\physical-local.yaml hybrid_meeting --dry-run
```

Apply the smoke sequence:

```powershell
workspace-fabric apply --config examples\physical-local.yaml desktop
workspace-fabric apply --config examples\physical-local.yaml work
workspace-fabric apply --config examples\physical-local.yaml hybrid_meeting
```

Inspect current driver state after each apply if needed:

```powershell
workspace-fabric state --config examples\physical-local.yaml
```

`state` is an inspection command. It must not replay saved hardware actions.

## Expected Routes

Observed video routes are reported by UHD-808 output port:

| Workspace | Expected UHD-808 routes |
| --- | --- |
| `desktop` | output `1` -> input `1`, output `2` -> input `2` |
| `work` | output `1` -> input `3`, output `2` -> input `4` |
| `hybrid_meeting` | output `1` -> input `1`, output `2` -> input `3` |

Observed USB routes are reported by UKM-404 device port:

| Workspace | Expected UKM-404 routes |
| --- | --- |
| `desktop` | `ukm404_a`: device `1` -> host `1`, device `2` -> host `1` |
| `work` | `ukm404_a`: device `1` -> host `2`, device `2` -> host `2` |
| `hybrid_meeting` | `ukm404_a`: device `1` -> host `1`, device `2` -> host `1`; `ukm404_b`: device `1` -> host `2`, device `2` -> host `2`, device `3` -> host `2` |

## Physical Confirmation

After each apply, confirm:

- The primary and secondary displays show the expected host outputs.
- The primary keyboard and mouse control the expected host.
- In `hybrid_meeting`, the webcam, drop microphone, and fingerprint reader are
  routed to the work laptop.
- The transaction result contains `observed_state` with `state_status:
  observed` for each driver that supports route query.

If a driver reports `unknown` or `last_known`, treat the physical route as not
fully verified even if the device appears to switch correctly.
