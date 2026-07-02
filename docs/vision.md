# Workspace Fabric Vision

## Vision Statement

Workspace Fabric exists to make technology disappear behind intent.

Modern workspaces are built from many independent systems: HDMI
matrices, USB switches, KVMs, management controllers, remote consoles,
virtual machines, audio devices, automation platforms, and countless
cables. Each solves one problem well, but together they create
complexity that users must continually manage.

Workspace Fabric seeks to replace that complexity with a unified control
plane.

Users should describe **what they want to accomplish**, not **how
signals should be routed**.

## The Problem

Today's workspaces are typically managed one device at a time.

-   Select an HDMI input.
-   Switch a USB matrix.
-   Open an iDRAC session.
-   Launch SSH.
-   Wake a sleeping workstation.
-   Change audio routing.

The operator understands the infrastructure because they have to.

Workspace Fabric shifts that responsibility to software.

## The Core Idea

Connect everything once.

Model every physical and virtual resource as part of a single fabric.

When an operator requests a workspace, scene, or action, Workspace
Fabric determines the best available path to satisfy that request.

That path may involve:

-   Physical HDMI switching
-   USB routing
-   Audio routing
-   Wake-on-LAN
-   BMC consoles (iDRAC, iLO, XClarity, IMM, Redfish)
-   Remote desktop technologies
-   Virtualization consoles
-   Toolkit actions
-   Automation workflows

The operator should not need to know which technologies were used.

## Guiding Principles

### Intent over implementation

The API should express user intent.

Example:

> "Work on the storage server."

Not:

> "Route HDMI input 4 to output 2."

### Hardware abstraction

Device-specific logic belongs in drivers.

The core fabric model should remain independent of vendors and
protocols.

### Transparency

Automation should never become mysterious.

Workspace Fabric should always be able to explain:

-   what it is doing
-   why it chose a particular path
-   what actions were taken
-   what failed

### Reliability

The control plane should continuously reconcile desired state with
observed state and recover gracefully from failures where possible.

### Extensibility

Every new hardware platform should be added through modular drivers
rather than modifications to the core architecture.

## What Workspace Fabric Is Not

Workspace Fabric is not simply:

-   another KVM
-   another HDMI matrix controller
-   another USB switch utility
-   another remote desktop launcher

It may include all of those capabilities, but its purpose is to unify
them into a coherent workspace experience.

## Long-Term Goal

Workspace Fabric should become the operating system for the modern
technical workspace.

Applications, automation platforms, AI assistants, and users should all
interact with the same logical model instead of directly controlling
individual devices.

## Success

Workspace Fabric succeeds when users stop thinking about cables, ports,
and protocols and instead think only about the work they want to
perform.

The fabric is responsible for everything in between.
