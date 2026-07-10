Phase 3: Physical Driver Integration

Milestone 3.1: Driver Contract Hardening
- Confirm video and USB driver interfaces are stable
- Document required driver methods
- Add driver capability/error expectations

Milestone 3.2: OREI UHD-808 Video Driver
- Implement TCP/Telnet or serial command transport
- Route video input to output
- Query current routing state if supported
- Add integration-safe tests with mocked transport

Milestone 3.3: OREI UKM-404 USB Driver
- Implement USB matrix routing
- Map device ports to host ports
- Query state if supported
- Add mocked transport tests

Milestone 3.4: Hardware Lab Config
- Create examples/test-lab.yaml or examples/physical-local.yaml
- Map real matrix ports to hosts, displays, and USB endpoints
- Use descriptive composite USB names where needed

Milestone 3.5: End-to-End Physical Smoke Test
- Apply desktop workspace
- Apply work workspace
- Apply hybrid meeting workspace
- Confirm physical video and USB routing changes
- Confirm observed state matches expected state
- Procedure: docs/hardware/physical-smoke-test.md

Milestone 3.6: Safety and Recovery
- Add dry-run-first recommendation
- Add timeout handling
- Add connection failure handling
- Add rollback/retry notes where practical
- Procedure: docs/hardware/safety-and-recovery.md
