"use client";

import { useEffect, useState } from "react";
import { 
  fetchSecuritySummary, 
  fetchVulnerabilities 
} from "@/lib/api";
import { 
  Card, 
  CardContent, 
  CardHeader, 
  CardTitle 
} from "@/components/ui/card";
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { 
  ShieldAlert, 
  ShieldCheck, 
  AlertOctagon, 
  AlertTriangle, 
  Info 
} from "lucide-react";

interface Vulnerability {
  id: number;
  source: string;
  severity: string;
  rule_id: string;
  description: string;
  file_path?: string;
  line_number?: number;
  remediation?: string;
  identified_at: string;
}

interface Summary {
  total_findings: int;
  counts_by_severity: Record<string, number>;
  counts_by_source: Record<string, number>;
}

export default function SecurityDashboard() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [vulnerabilities, setVulnerabilities] = useState<Vulnerability[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [summaryData, vulnsData] = await Promise.all([
          fetchSecuritySummary(),
          fetchVulnerabilities()
        ]);
        setSummary(summaryData);
        setVulnerabilities(vulnsData.vulnerabilities || []);
      } catch (err) {
        console.error("Failed to load security data", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const getSeverityBadge = (severity: string) => {
    switch (severity.toLowerCase()) {
      case "critical": return <Badge className="bg-red-600">Critical</Badge>;
      case "high": return <Badge className="bg-orange-500">High</Badge>;
      case "medium": return <Badge className="bg-yellow-500 text-black">Medium</Badge>;
      case "low": return <Badge className="bg-blue-500">Low</Badge>;
      default: return <Badge variant="outline">Info</Badge>;
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity.toLowerCase()) {
      case "critical": return <AlertOctagon className="text-red-600" size={20} />;
      case "high": return <AlertTriangle className="text-orange-500" size={20} />;
      case "medium": return <AlertTriangle className="text-yellow-500" size={20} />;
      default: return <Info className="text-blue-500" size={20} />;
    }
  };

  if (loading) return <div className="p-8">Loading security posture...</div>;

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold tracking-tight text-slate-900">Security Posture</h2>
        <p className="text-slate-500 mt-1">Unified security monitoring and vulnerability tracking</p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card className="border-red-200 bg-red-50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-red-900 uppercase">Critical</CardTitle>
            <AlertOctagon className="text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-700">
              {summary?.counts_by_severity.critical || 0}
            </div>
          </CardContent>
        </Card>
        
        <Card className="border-orange-200 bg-orange-50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-orange-900 uppercase">High</CardTitle>
            <AlertTriangle className="text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-700">
              {summary?.counts_by_severity.high || 0}
            </div>
          </CardContent>
        </Card>

        <Card className="border-yellow-200 bg-yellow-50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-yellow-900 uppercase">Medium</CardTitle>
            <AlertTriangle className="text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-700">
              {summary?.counts_by_severity.medium || 0}
            </div>
          </CardContent>
        </Card>

        <Card className="border-blue-200 bg-blue-50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-blue-900 uppercase">Total Findings</CardTitle>
            <ShieldAlert className="text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-700">
              {summary?.total_findings || 0}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="bg-white shadow-sm">
        <CardHeader>
          <CardTitle>Vulnerability Details</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Severity</TableHead>
                <TableHead>Source</TableHead>
                <TableHead>Rule/ID</TableHead>
                <TableHead className="w-1/3">Description</TableHead>
                <TableHead>File</TableHead>
                <TableHead>Detected At</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {vulnerabilities.map((vuln) => (
                <TableRow key={vuln.id}>
                  <TableCell>{getSeverityBadge(vuln.severity)}</TableCell>
                  <TableCell>
                    <Badge variant="outline" className="uppercase">{vuln.source}</Badge>
                  </TableCell>
                  <TableCell className="font-mono text-xs">{vuln.rule_id}</TableCell>
                  <TableCell className="text-sm">{vuln.description}</TableCell>
                  <TableCell className="text-xs text-slate-500">
                    {vuln.file_path ? `${vuln.file_path}:${vuln.line_number}` : "N/A"}
                  </TableCell>
                  <TableCell className="text-xs">
                    {new Date(vuln.identified_at).toLocaleDateString()}
                  </TableCell>
                </TableRow>
              ))}
              {vulnerabilities.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8 text-slate-400">
                    <div className="flex flex-col items-center gap-2">
                      <ShieldCheck className="text-green-500 h-8 w-8" />
                      <span>No active vulnerabilities found.</span>
                    </div>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
