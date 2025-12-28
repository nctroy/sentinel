import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Activity, Clock } from "lucide-react";

interface AgentCardProps {
  id: string;
  domain: string;
  status: "idle" | "working" | "error";
  lastActive: string;
}

import Link from "next/link";

// ... existing imports

export function AgentCard({ id, domain, status, lastActive }: AgentCardProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case "working": return "bg-green-500 hover:bg-green-600";
      case "error": return "bg-red-500 hover:bg-red-600";
      default: return "bg-slate-500 hover:bg-slate-600";
    }
  };

  return (
    <Link href={`/agents/${id}`}>
      <Card className="hover:shadow-md transition-shadow cursor-pointer">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium uppercase tracking-wider text-slate-500">
            {domain}
          </CardTitle>
          <Badge className={getStatusColor(status)}>
            {status}
          </Badge>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold mb-1">{id}</div>
          <div className="flex items-center text-xs text-slate-500 gap-1">
            <Clock size={12} />
            <span>Last active: {lastActive}</span>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
