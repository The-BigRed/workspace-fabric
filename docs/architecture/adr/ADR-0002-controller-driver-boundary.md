# ADR-0002: Controller and Driver Boundary

## Status
Accepted

## Context
The seed configuration originally used a top-level `drivers` section for configured physical devices. That created ambiguity because the word "driver" can mean either a code module in the repository or a configured hardware instance in a deployment.

Multiple physical devices may use the same code driver. For example, two OREI UKM404 USB matrices should both use the same `orei-ukm404` driver implementation while having separate network addresses and configuration.

## Decision
Workspace Fabric will distinguish between **drivers** and **controllers**.

- **Driver** means the code-level implementation.
- **Controller** means a configured, reachable instance of that driver.

Example:

```yaml
controllers:
  usb_matrix_ukm404_a:
    driver: orei-ukm404
    transport: telnet
    host: 192.0.2.10
    port: 23

  usb_matrix_ukm404_b:
    driver: orei-ukm404
    transport: telnet
    host: 192.0.2.11
    port: 23
```

Hardware topology should then reference the configured controller instance:

```yaml
hardware:
  usb_matrices:
    ukm404_a:
      controller: usb_matrix_ukm404_a
```

## Rationale
This terminology avoids overloading `driver` and makes the configuration easier to read:

- `driver` answers: "Which code implementation should be used?"
- `controller` answers: "Which configured physical or software instance should be contacted?"
- `hardware` answers: "How is this controller wired into the physical lab?"

## Consequences
- Public example YAML should prefer `controllers:` over a top-level `drivers:` section for configured devices.
- Multiple controllers may share one driver.
- Driver names should remain stable code identifiers.
- Controller names should be deployment-specific stable instance identifiers.
