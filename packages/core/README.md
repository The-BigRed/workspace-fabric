# Workspace Fabric Core

Workspace Fabric Core contains the orchestration, configuration, planning,
transaction, and generic driver-discovery infrastructure for Workspace Fabric.

Driver implementations are distributed separately. The core package may depend
on the shared Workspace Fabric Driver API, but it does not contain or import
mock, OREI UHD-808, OREI UKM404, or other implementation driver packages.
