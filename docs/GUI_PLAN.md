# Sentinel Command Center - GUI Development Plan

## Phase 1: Foundation (Scaffolding)
- [x] **Initialize Next.js Project**
    - Create `web/` directory.
    - Setup TypeScript, Tailwind CSS, ESLint.
- [x] **UI Component Library Setup**
    - Install `shadcn/ui` base.
    - Install essential components: `Card`, `Button`, `Badge`, `Table`, `Alert`.
    - Install `lucide-react` for icons.
- [x] **Backend Configuration**
    - Update `src/mcp_server/sentinel_server.py` to enable CORS.
    - Ensure all necessary endpoints (`/agents`, `/diagnose`, `/execute`) are exposed.

## Phase 2: Core Components & Layout
- [x] **App Layout**
    - Sidebar navigation (Dashboard, Agents, Settings).
    - Header with connection status indicator.
- [x] **Dashboard View**
    - **Status Overview:** Grid of `AgentCard`s showing health and current state.
    - **Bottleneck Feed:** List of recent findings with "Impact Score" badges.
    - **Quick Actions:** "Run Diagnostic Cycle" button.
- [ ] **Agent Detail View**
    - Deep dive into a specific agent's history and logs.
    - Manual control to trigger specific actions.

## Phase 3: Integration (Connecting Frontend to Backend)
- [x] **API Client**
    - Create typed API hooks (e.g., `useAgents`, `useSystemStatus`).
- [ ] **Real-time Updates**
    - Implement polling or WebSocket (if needed) for agent status updates.
- [x] **Action Wiring**
    - Connect "Run Cycle" button to `/orchestrate` endpoint.
    - Connect "Fix" buttons to `/execute` endpoint.

## Phase 4: Polish & Experience
- [ ] **Dark Mode:** Ensure full support for system preference.
- [ ] **Error Handling:** Graceful toasts/notifications for API failures.
- [ ] **Empty States:** Helpful guides when no agents are registered.
