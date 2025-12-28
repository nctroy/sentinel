"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { fetchAgentState, runDiagnosis } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowLeft, Play, RefreshCw, Activity, Database, Shield } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export default function AgentDetailPage() {
    const params = useParams();
    const router = useRouter();
    const id = params.id as string;

    const [agentState, setAgentState] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [running, setRunning] = useState(false);

    const loadState = async () => {
        try {
            setLoading(true);
            const data = await fetchAgentState(id);
            setAgentState(data.state);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (id) loadState();
    }, [id]);

    const handleRunDiagnosis = async () => {
        if (!agentState) return;
        try {
            setRunning(true);
            await runDiagnosis(id, agentState.domain);
            await loadState();
        } catch (error) {
            console.error(error);
        } finally {
            setRunning(false);
        }
    };

    if (loading) {
        return <div className="p-8 text-center text-slate-500">Loading agent details...</div>;
    }

    if (!agentState) {
        return (
            <div className="p-8 text-center">
                <h2 className="text-xl font-bold text-slate-900">Agent Not Found</h2>
                <Button variant="link" onClick={() => router.push('/')}>Return to Dashboard</Button>
            </div>
        );
    }

    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <Button variant="ghost" size="icon" onClick={() => router.push('/')}>
                        <ArrowLeft size={20} />
                    </Button>
                    <div>
                        <h2 className="text-3xl font-bold tracking-tight text-slate-900">{agentState.name || id}</h2>
                        <div className="flex items-center gap-2 text-slate-500 mt-1">
                            <Badge variant="secondary">{agentState.domain}</Badge>
                            <span className="text-sm">•</span>
                            <span className="text-sm">Last Run: {new Date(agentState.last_run).toLocaleString()}</span>
                        </div>
                    </div>
                </div>
                <div className="flex gap-2">
                    <Button variant="outline" size="icon" onClick={loadState}>
                        <RefreshCw size={16} />
                    </Button>
                    <Button onClick={handleRunDiagnosis} disabled={running}>
                        <Play size={16} className="mr-2" />
                        {running ? "Running..." : "Run Diagnosis"}
                    </Button>
                </div>
            </div>

            <div className="grid gap-6 md:grid-cols-3">
                <Card className="col-span-1">
                    <CardHeader>
                        <CardTitle className="text-lg flex items-center gap-2">
                            <Activity size={20} className="text-sky-500" />
                            Metrics
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            {Object.entries(agentState.metrics || {}).map(([key, value]) => (
                                <div key={key} className="flex justify-between items-center bg-slate-50 p-3 rounded-lg">
                                    <span className="text-sm font-medium capitalize text-slate-600">
                                        {key.replace(/_/g, ' ')}
                                    </span>
                                    <span className="text-lg font-bold text-slate-900">{String(value)}</span>
                                </div>
                            ))}
                            {Object.keys(agentState.metrics || {}).length === 0 && (
                                <div className="text-sm text-slate-500 italic">No metrics recorded yet</div>
                            )}
                        </div>
                    </CardContent>
                </Card>

                <Card className="col-span-2">
                    <CardHeader>
                        <CardTitle className="text-lg flex items-center gap-2">
                            <Database size={20} className="text-violet-500" />
                            Configuration
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="p-4 border rounded-lg">
                                <div className="text-sm text-slate-500 mb-1">Agent ID</div>
                                <div className="font-mono text-sm">{agentState.agent_id}</div>
                            </div>
                            <div className="p-4 border rounded-lg">
                                <div className="text-sm text-slate-500 mb-1">Domain</div>
                                <div className="font-medium">{agentState.domain}</div>
                            </div>
                        </div>

                        <div className="mt-6">
                            <h4 className="font-medium mb-3 flex items-center gap-2">
                                <Shield size={16} /> Responsibilities
                            </h4>
                            <ul className="list-disc list-inside text-sm text-slate-600 space-y-1 ml-2">
                                {/* Note: Responsibilities aren't in /state api yet, but good to have a placeholder or add later */}
                                <li>Monitor domain specific events</li>
                                <li>Identify bottlenecks and blockers</li>
                                <li>Execute approved actions</li>
                            </ul>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
