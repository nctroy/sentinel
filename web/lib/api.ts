const API_BASE_URL = "http://localhost:8000";

export async function fetchAgents() {
  const response = await fetch(`${API_BASE_URL}/agents`);
  if (!response.ok) {
    throw new Error("Failed to fetch agents");
  }
  return response.json();
}

export async function fetchReports() {
  const response = await fetch(`${API_BASE_URL}/reports`);
  if (!response.ok) {
    throw new Error("Failed to fetch reports");
  }
  return response.json();
}

export async function runDiagnosis(agentId: string, domain: string) {
  const response = await fetch(`${API_BASE_URL}/diagnose`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ agent_id: agentId, domain }),
  });
  if (!response.ok) {
    throw new Error("Failed to run diagnosis");
  }
  return response.json();
}

export async function runOrchestration() {
  const response = await fetch(`${API_BASE_URL}/orchestrate`, {
    method: "POST",
  });
  if (!response.ok) {
    throw new Error("Failed to run orchestration cycle");
  }
  return response.json();
}

export async function fetchAgentState(agentId: string) {
  const response = await fetch(`${API_BASE_URL}/state`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ agent_id: agentId }),
  });
  if (!response.ok) {
    throw new Error("Failed to fetch agent state");
  }
  return response.json();
}
