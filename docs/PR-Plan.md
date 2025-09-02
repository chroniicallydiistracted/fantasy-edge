# PR Plan

1. **Add SSE client for live updates**
   - Scope: create EventSource client that connects to `/live/subscribe` and surfaces messages.
   - Test Plan: `npm test` and manual verification of live events in browser console.
   - Acceptance: frontend receives heartbeat events without page reload.
