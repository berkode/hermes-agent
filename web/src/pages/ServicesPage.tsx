import { useCallback, useEffect, useState } from "react";
import { Play, Power, RefreshCw, Server, Square } from "lucide-react";
import { api } from "@/lib/api";
import type { ServicesStatusResponse } from "@/lib/api";
import { Button } from "@nous-research/ui/ui/components/button";
import { Badge } from "@nous-research/ui/ui/components/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Spinner } from "@nous-research/ui/ui/components/spinner";
import { useToast } from "@/hooks/useToast";
import { Toast } from "@/components/Toast";
import { useI18n } from "@/i18n";

const SERVICE_META: Record<string, { title: string; desc: string }> = {
  "hermes-dashboard": {
    title: "Hermes dashboard",
    desc: ":8000 — fleet control + Chat (replaces central agency)",
  },
  "hermes-gateway": {
    title: "Hermes gateway",
    desc: "Cron + messaging (manual)",
  },
  nginx: { title: "nginx", desc: ":80 → dashboard upstream (MacPorts)" },
  ollama: { title: "Ollama", desc: ":11434 — local models" },
  ngrok: { title: "ngrok", desc: "Tunnel to nginx :80" },
  agency: { title: "Agency API", desc: ":8088 — webhooks, /api/agents, monitor (Hermes UI on :8000)" },
  pimono: { title: "Pimono", desc: "pi-ai :3099 — BejMind API keys" },
  "pimono-proxy": { title: "OpenAI proxy", desc: ":5102 — Hermes LLM endpoint" },
  bejmind: { title: "BejMind", desc: ":5002 — debate / consult" },
  bejtrader: { title: "BejTrader", desc: ":5001 — trading API" },
  nautilus: { title: "Nautilus", desc: ":5011 — status bridge" },
  predictx: { title: "PredictX", desc: ":5004 — prediction markets" },
};

const SERVICE_ORDER = [
  "hermes-dashboard",
  "hermes-gateway",
  "nginx",
  "ollama",
  "ngrok",
  "agency",
  "pimono",
  "pimono-proxy",
  "bejmind",
  "bejtrader",
  "nautilus",
  "predictx",
];

export default function ServicesPage() {
  const { t } = useI18n();
  const { toast, showToast } = useToast();
  const [status, setStatus] = useState<ServicesStatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState<string | null>(null);
  const [log, setLog] = useState("");

  const appendLog = (msg: string) => {
    setLog((prev) => `${new Date().toLocaleTimeString()} — ${msg}\n${prev}`.slice(0, 4000));
  };

  const refresh = useCallback(async () => {
    try {
      const data = await api.getServicesStatus();
      setStatus(data);
    } catch (e) {
      const message = e instanceof Error ? e.message : String(e);
      setStatus({ services: {}, error: message, available: false });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
    const id = window.setInterval(() => void refresh(), 5000);
    return () => window.clearInterval(id);
  }, [refresh]);

  const runBulk = async (action: "start-llm" | "start-all" | "stop-all") => {
    setBusy(action);
    try {
      const res = await api.postServicesBulk(action);
      setStatus(res.status);
      appendLog(res.message || action);
      showToast(res.message || action, res.ok ? "success" : "error");
    } catch (e) {
      const message = e instanceof Error ? e.message : String(e);
      appendLog(message);
      showToast(message, "error");
    } finally {
      setBusy(null);
    }
  };

  const runService = async (
    action: "start" | "stop" | "toggle",
    service: string,
  ) => {
    const key = `${action}:${service}`;
    setBusy(key);
    try {
      const res = await api.postServicesPerService(action, service);
      setStatus(res.status);
      appendLog(res.message || key);
      showToast(res.message || key, res.ok ? "success" : "error");
    } catch (e) {
      const message = e instanceof Error ? e.message : String(e);
      appendLog(message);
      showToast(message, "error");
    } finally {
      setBusy(null);
    }
  };

  const services = status?.services ?? {};
  const unavailable = status?.available === false;

  return (
    <div className="flex flex-col gap-4 p-4 md:p-6 max-w-2xl">
      <p className="text-sm text-muted-foreground">{t.services.subtitle}</p>
      <p className="text-sm text-muted-foreground">{t.services.manualNote}</p>

      {status?.error && (
        <p className="text-sm text-destructive">{status.error}</p>
      )}

      <div className="flex flex-wrap gap-2">
        <Button
          size="sm"
          disabled={!!busy || unavailable}
          onClick={() => void runBulk("start-llm")}
        >
          {busy === "start-llm" ? <Spinner className="mr-1 h-3 w-3" /> : <Play className="mr-1 h-3.5 w-3.5" />}
          {t.services.startLlm}
        </Button>
        <Button
          size="sm"
          ghost
          disabled={!!busy || unavailable}
          onClick={() => void runBulk("start-all")}
        >
          {t.services.startAll}
        </Button>
        <Button
          size="sm"
          ghost
          className="text-destructive"
          disabled={!!busy || unavailable}
          onClick={() => void runBulk("stop-all")}
        >
          {t.services.stopAll}
        </Button>
        <Button
          size="sm"
          ghost
          disabled={!!busy}
          onClick={() => void refresh()}
        >
          <RefreshCw className="mr-1 h-3.5 w-3.5" />
          {t.common.refresh}
        </Button>
      </div>

      {loading && !status ? (
        <div className="flex items-center gap-2 text-muted-foreground">
          <Spinner />
          {t.common.loading}
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {SERVICE_ORDER.map((key) => {
            const up = services[key] === true;
            const meta = SERVICE_META[key] ?? { title: key, desc: "" };
            const isBusy = busy === `start:${key}` || busy === `stop:${key}` || busy === `toggle:${key}`;
            return (
              <Card key={key}>
                <CardContent className="flex flex-col gap-3 p-4 sm:flex-row sm:items-center sm:justify-between">
                  <div className="flex items-start gap-3 min-w-0">
                    <Server className="h-5 w-5 shrink-0 text-primary mt-0.5" />
                    <div className="min-w-0">
                      <div className="font-medium">{meta.title}</div>
                      <div className="text-xs text-muted-foreground">{meta.desc}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <Badge tone={up ? "success" : "secondary"}>
                      {up ? t.services.up : t.services.down}
                    </Badge>
                    <Button
                      size="sm"
                      ghost
                      disabled={!!busy || unavailable}
                      onClick={() => void runService("toggle", key)}
                    >
                      {isBusy ? (
                        <Spinner className="h-3 w-3" />
                      ) : up ? (
                        <Square className="h-3.5 w-3.5" />
                      ) : (
                        <Power className="h-3.5 w-3.5" />
                      )}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {log ? (
        <pre className="text-xs text-muted-foreground whitespace-pre-wrap font-mono max-h-32 overflow-auto rounded-md border border-border p-2">
          {log}
        </pre>
      ) : null}

      <Toast toast={toast} />
    </div>
  );
}
