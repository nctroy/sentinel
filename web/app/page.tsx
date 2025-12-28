"use client";

import { useState } from "react";
import useSWR, { mutate } from "swr";
import { AgentCard } from "@/components/dashboard/AgentCard";
import { BottleneckList } from "@/components/dashboard/BottleneckList";
import { Button } from "@/components/ui/button";
import { Play, RefreshCw, AlertCircle } from "lucide-react";
import { fetchAgents, fetchReports, runOrchestration } from "@/lib/api";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

const FETCH_AGENTS_KEY = "/agents";
const FETCH_REPORTS_KEY = "/reports";

export default function Dashboard() {
  const [isRunning, setIsRunning] = useState(false);
  const [cycleError, setCycleError] = useState<string | null>(null);

  // SWR Hooks for polling
  const { data: agentsData, error: agentsError, isLoading: agentsLoading } = useSWR(FETCH_AGENTS_KEY, fetchAgents, { refreshInterval: 2000 });
  const { data: reportsData, error: reportsError, isLoading: reportsLoading } = useSWR(FETCH_REPORTS_KEY, fetchReports, { refreshInterval: 2000 });

  const agents = agentsData?.agents || [];
  const reports = reportsData?.reports || [];

  const loading = agentsLoading || reportsLoading;
  const connectionError = agentsError || reportsError;

  const handleRunCycle = async () => {
    try {
      setIsRunning(true);
      setCycleError(null);
      await runOrchestration();
      // Trigger immediate re-fetch
      mutate(FETCH_AGENTS_KEY);
      mutate(FETCH_REPORTS_KEY);
    } catch (err: any) {
      console.error(err);
      setCycleError(err.message || "Failed to run cycle");
    } finally {
      setIsRunning(false);
    }
  };

  const formatLastRun = (dateString?: string) => {
    if (!dateString) return "Never";
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-slate-900">Chief of Staff</h2>
          <p className="text-slate-500 mt-1">Orchestration & Intelligence Dashboard</p>
        </div>
        <div className="flex gap-2">
          {/* Spinning refresh icon to show polling is active/alive */}
          {loading && <RefreshCw size={16} className="animate-spin text-slate-400 self-center mr-2" />}

          <Button className="gap-2" onClick={handleRunCycle} disabled={isRunning || !!connectionError}>
            <Play size={16} />
            {isRunning ? "Running Cycle..." : "Run Diagnostic Cycle"}
          </Button>
        </div>
      </div>

      {connectionError && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Connection Error</AlertTitle>
          <AlertDescription>
            Could not connect to Sentinel Server. Ensure backend is running at localhost:8000.
          </AlertDescription>
        </Alert>
      )}

      {cycleError && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Cycle Failed</AlertTitle>
          <AlertDescription>{cycleError}</AlertDescription>
        </Alert>
      )}

      <div className="grid gap-4 md:grid-cols-3">
        {agents.map((agent: any) => (
          <AgentCard
            key={agent.agent_id}
            id={agent.agent_id}
            domain={agent.domain}
            status={isRunning ? "working" : "idle"}
            lastActive={formatLastRun(agent.last_run)}
          />
        ))}
        {!loading && agents.length === 0 && !connectionError && (
          <div className="col-span-3 text-center p-8 border rounded-lg border-dashed text-slate-400">
            No agents registered. Run <code>init-project</code> in CLI.
          </div>
        )}
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <div className="col-span-4 border rounded-xl p-6 bg-white shadow-sm">
          <h3 className="font-semibold text-lg mb-4">Live Activity</h3>
          <div className="text-slate-500 text-sm">
            Activity polling enabled (2s). Watch terminal for detailed logs.
          </div>
        </div>
        <div className="col-span-3 border rounded-xl p-6 bg-white shadow-sm">
          <h3 className="font-semibold text-lg mb-4">Active Bottlenecks</h3>
          <BottleneckList reports={reports} />
        </div>
      </div>
    </div>
  );
}
