import { Badge } from "@/components/ui/badge";
import { AlertTriangle, CheckCircle2 } from "lucide-react";

interface Bottleneck {
  description: string;
  impact_score: number;
  confidence: number;
}

interface Report {
  agent_id: string;
  bottleneck: Bottleneck | null;
}

export function BottleneckList({ reports }: { reports: Report[] }) {
  const activeBottlenecks = reports.filter(r => r.bottleneck !== null);

  if (activeBottlenecks.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-8 text-slate-500">
        <CheckCircle2 className="h-8 w-8 mb-2 text-green-500" />
        <p>All systems healthy. No bottlenecks detected.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {activeBottlenecks.map((report) => (
        <div
          key={report.agent_id}
          className="flex items-start gap-4 p-4 rounded-lg bg-yellow-50 border border-yellow-200"
        >
          <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5 shrink-0" />
          <div className="flex-1 space-y-1">
            <div className="flex items-center justify-between">
              <h4 className="font-semibold text-sm text-yellow-900 uppercase tracking-wide">
                {report.agent_id}
              </h4>
              <div className="flex gap-2">
                <Badge variant="outline" className="bg-white text-slate-600 border-slate-200">
                   Impact: {report.bottleneck?.impact_score}/10
                </Badge>
                <Badge variant="outline" className="bg-white text-slate-600 border-slate-200">
                   {((report.bottleneck?.confidence || 0) * 100).toFixed(0)}% Conf.
                </Badge>
              </div>
            </div>
            <p className="text-sm text-yellow-800">
              {report.bottleneck?.description}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}
