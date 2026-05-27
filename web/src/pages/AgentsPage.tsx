import { useCallback, useEffect, useState } from "react";
import { Bot, RefreshCw } from "lucide-react";
import { api, type AgentRunRow, type AgentsListResponse } from "@/lib/api";
import { Button } from "@nous-research/ui/ui/components/button";
import { Badge } from "@nous-research/ui/ui/components/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Spinner } from "@nous-research/ui/ui/components/spinner";
import { useToast } from "@/hooks/useToast";
import { Toast } from "@/components/Toast";
import { useI18n } from "@/i18n";

export default function AgentsPage() {
  const { t } = useI18n();
  const { toast, showToast } = useToast();
  const [data, setData] = useState<AgentsListResponse | null>(null);
  const [capabilities, setCapabilities] = useState<string[]>([]);
  const [selected, setSelected] = useState<unknown | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);

  const refresh = useCallback(async () => {
    try {
      const [runsRes, capsRes] = await Promise.all([
        api.getAgentRuns(),
        api.getAgentCapabilities().catch(() => null),
      ]);
      setData(runsRes);
      if (capsRes?.capabilities) {
        setCapabilities(capsRes.capabilities.map((c) => c.name));
      }
    } catch (e) {
      const message = e instanceof Error ? e.message : String(e);
      setData({ runs: [], error: message, available: false });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
    const id = window.setInterval(() => void refresh(), 8000);
    return () => window.clearInterval(id);
  }, [refresh]);

  const createDemo = async () => {
    setBusy(true);
    try {
      await api.createAgentRun({
        runtime: "hermes",
        workflow: "monitoring",
        summary: "Hermes dashboard probe run",
        tasks: ["monitor"],
      });
      showToast("Agent run created", "success");
      await refresh();
    } catch (e) {
      showToast(e instanceof Error ? e.message : String(e), "error");
    } finally {
      setBusy(false);
    }
  };

  const loadDetail = async (runId: string) => {
    try {
      const detail = await api.getAgentRun(runId);
      setSelected(detail);
    } catch (e) {
      showToast(e instanceof Error ? e.message : String(e), "error");
    }
  };

  const runs = data?.runs ?? [];
  const blocked = runs.filter((r) => r.status === "blocked");
  const unavailable = data?.available === false;

  return (
    <div className="flex flex-col gap-4 p-4 md:p-6 max-w-3xl">
      <p className="text-sm text-muted-foreground">
        Bejcapital agent runs via agency API ({capabilities.length ? `${capabilities.length} capabilities` : "start agency on :8088"}).
        Fleet control stays on Services.
      </p>
      {data?.error && <p className="text-sm text-destructive">{data.error}</p>}

      <div className="flex flex-wrap gap-2">
        <Button size="sm" disabled={busy || unavailable} onClick={() => void createDemo()}>
          {busy ? <Spinner className="mr-1 h-3 w-3" /> : <Bot className="mr-1 h-3.5 w-3.5" />}
          New run
        </Button>
        <Button size="sm" ghost disabled={loading} onClick={() => void refresh()}>
          <RefreshCw className="mr-1 h-3.5 w-3.5" />
          {t.common.refresh}
        </Button>
      </div>

      {blocked.length > 0 && (
        <p className="text-sm text-amber-600 dark:text-amber-400">
          {blocked.length} blocked run(s) awaiting operator approval via agency API.
        </p>
      )}

      {loading && !data ? (
        <div className="flex items-center gap-2 text-muted-foreground">
          <Spinner />
          {t.common.loading}
        </div>
      ) : runs.length === 0 ? (
        <p className="text-sm text-muted-foreground">
          No agent runs yet. Toggle <strong>Agency API</strong> on the Services tab or run{" "}
          <code className="text-xs">./main start agency --background</code> with <code className="text-xs">AGENCY_PORT=8088</code>.
        </p>
      ) : (
        <div className="flex flex-col gap-3">
          {runs.map((run: AgentRunRow) => (
            <Card key={run.run_id} className="cursor-pointer" onClick={() => void loadDetail(run.run_id)}>
              <CardContent className="flex flex-col gap-2 p-4 sm:flex-row sm:items-center sm:justify-between">
                <div className="min-w-0">
                  <div className="font-medium truncate">{run.workflow}</div>
                  <div className="text-xs text-muted-foreground truncate">
                    {run.runtime} · {run.run_id.slice(0, 8)}…
                  </div>
                  {run.summary ? (
                    <div className="text-xs text-muted-foreground mt-1">{run.summary}</div>
                  ) : null}
                </div>
                <Badge
                  tone={
                    run.status === "success"
                      ? "success"
                      : run.status === "blocked"
                        ? "destructive"
                        : "secondary"
                  }
                >
                  {run.status}
                </Badge>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {selected ? (
        <pre className="text-xs whitespace-pre-wrap font-mono max-h-48 overflow-auto rounded-md border border-border p-2">
          {JSON.stringify(selected, null, 2)}
        </pre>
      ) : null}

      <Toast toast={toast} />
    </div>
  );
}
