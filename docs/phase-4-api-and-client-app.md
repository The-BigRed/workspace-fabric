Phase 4: API and Client Interface

4.1 API service
- FastAPI or similar HTTP service
- endpoints for config, graph, workspace list, apply, state
- structured errors and transaction IDs

4.2 API auth and safety
- local-only/default bind
- token auth
- read-only vs operator permissions
- dry-run support

4.3 Client app
- simple web UI or desktop UI
- list workspaces
- preview apply plan
- apply workspace
- show current state

4.4 Automation integration
- REST API documentation
- Home Assistant/OpenClaw-friendly endpoints
- later webhook/event support
