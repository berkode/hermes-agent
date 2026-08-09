"""Manual start/stop for Bejcapital fleet + Hermes (no LaunchAgents).

Replaces the legacy central agency UI on :8000 with ``hermes dashboard``.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any, Callable, Optional

from hermes_constants import get_hermes_home

# Ollama runs on Oracle VM only — Mac reaches it via oracle-llm-tunnel.sh (see start_one pimono).
_LOCAL_INFRA: list[str] = ["nginx", "ngrok", "camofox-browser"]
_CLOUD_INFRA: list[str] = ["cloudflared", "ollama", "camofox-browser"]
_CORE_SERVICES: list[str] = [
    "hermes-dashboard",
    "hermes-gateway",
    "agency",
    "pimono",
    "pimono-proxy",
    "bejmind",
    "bejtrader",
    "nautilus",
    "predictx",
]

INFRA_SERVICES = frozenset({"nginx", "ollama", "ngrok", "cloudflared"})
AGENCY_API_SERVICES = frozenset({"agency"})
PLATFORM_SERVICES = frozenset({"bejmind", "bejtrader", "nautilus", "predictx"})
HERMES_SERVICES = frozenset({"hermes-dashboard", "hermes-gateway", "pimono", "pimono-proxy"})

def oracle_llm_on_mac() -> bool:
    """Mac Hermes LLM (Pimono/Ollama/gemma) is served from Oracle VM via SSH tunnel."""
    if deploy_profile() == "cloud":
        return False
    raw = (
        os.environ.get("BEJCAPITAL_ORACLE_LLM")
        or os.environ.get("HERMES_ORACLE_LLM")
        or "1"
    ).strip().lower()
    return raw not in ("0", "false", "no", "off")


def deploy_profile() -> str:
    """local = Mac (nginx + ngrok). cloud = Oracle/Linux (cloudflared → agency :8088)."""
    raw = (
        os.environ.get("BEJCAPITAL_DEPLOY_PROFILE")
        or os.environ.get("DEPLOY_PROFILE")
        or ""
    ).strip().lower()
    if raw == "cloud":
        return "cloud"
    if raw == "local":
        return "local"
    if sys.platform == "linux":
        return "cloud"
    return "local"


def service_order() -> list[str]:
    infra = _CLOUD_INFRA if deploy_profile() == "cloud" else _LOCAL_INFRA
    return [
        "hermes-dashboard",
        "hermes-gateway",
        *infra,
        *[s for s in _CORE_SERVICES if s not in ("hermes-dashboard", "hermes-gateway")],
    ]


# Back-compat for imports; prefer service_order() at runtime.
SERVICE_ORDER: list[str] = service_order()

KNOWN_SERVICES = frozenset(service_order())


def bejcapital_root() -> Path:
    return Path(
        os.environ.get("BEJCAPITAL_ROOT", Path.home() / "berkode" / "bejcapital")
    ).expanduser()


def hermes_agent_root() -> Path:
    return Path(
        os.environ.get("HERMES_AGENT_ROOT", Path(__file__).resolve().parents[1])
    ).expanduser()


def hermes_home() -> Path:
    return get_hermes_home()


def run_dir() -> Path:
    d = hermes_home() / "run"
    d.mkdir(parents=True, exist_ok=True)
    return d


def log_dir() -> Path:
    d = hermes_home() / "logs"
    d.mkdir(parents=True, exist_ok=True)
    return d


def dashboard_port() -> int:
    raw = os.environ.get("HERMES_DASHBOARD_PORT", "").strip()
    if raw.isdigit():
        return int(raw)
    try:
        from hermes_cli.config import load_config

        port = (load_config().get("dashboard") or {}).get("port")
        if port is not None:
            return int(port)
    except Exception:
        pass
    return 8000


def camofox_port() -> int:
    raw = os.environ.get("CAMOFOX_PORT", "").strip()
    if raw.isdigit():
        return int(raw)
    return 9377


def camofox_root() -> Path:
    explicit = os.environ.get("CAMOFOX_ROOT", "").strip()
    if explicit:
        return Path(explicit).expanduser()
    return bejcapital_root() / "external" / "camofox-browser"


def agency_api_port() -> int:
    raw = os.environ.get("BEJCAPITAL_AGENCY_PORT", "").strip()
    if raw.isdigit():
        return int(raw)
    # Hermes dashboard on :8000 — agency API defaults to :8088
    if dashboard_port() == 8000:
        return 8088
    return 8088


def agency_health_url() -> str:
    base = os.environ.get("BEJCAPITAL_AGENCY_URL", "").strip().rstrip("/")
    if base:
        return base if base.endswith("/health") else f"{base}/health"
    return f"http://127.0.0.1:{agency_api_port()}/health"


def _health(url: str, timeout: float = 2.0) -> bool:
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return 200 <= resp.status < 400
    except Exception:
        return False


def _pid_alive(pid_file: Path) -> bool:
    if not pid_file.is_file():
        return False
    try:
        pid = int(pid_file.read_text().strip())
    except (ValueError, OSError):
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _bejcapital_python() -> Path:
    root = bejcapital_root()
    candidate = root / "app" / ".venv" / "bin" / "python"
    return candidate if candidate.is_file() else Path(sys.executable)


def _run_in_bejcapital(argv: list[str], *, timeout: int = 180) -> tuple[int, str]:
    root = bejcapital_root()
    main_sh = root / "main"
    if not main_sh.is_file():
        return 1, f"Missing {main_sh}"
    proc = subprocess.run(
        ["bash", str(main_sh), *argv],
        cwd=str(root),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    out = ((proc.stdout or "") + (proc.stderr or "")).strip()
    return proc.returncode, out


def _infra_mgr(action: str, name: str) -> tuple[int, str]:
    """action: check | start | stop"""
    root = bejcapital_root()
    if not (root / "app" / "agency" / "service_manager.py").is_file():
        return 1, f"Missing bejcapital at {root}"
    py = _bejcapital_python()
    snippet = f"""
import sys
sys.path.insert(0, {str(root)!r})
from app.agency.service_manager import (
    check_service,
    start_service,
    stop_service,
    _load_services_yaml,
)
specs = _load_services_yaml()
spec = specs.get({name!r})
if not spec:
    raise SystemExit(f"no spec for {{name!r}}")
if {action!r} == "check":
    import json
    print(json.dumps(check_service({name!r}, spec)))
elif {action!r} == "start":
    ok, msg = start_service({name!r}, spec)
    print(msg)
    raise SystemExit(0 if ok else 1)
else:
    ok, msg = stop_service({name!r}, spec)
    print(msg)
    raise SystemExit(0 if ok else 1)
"""
    proc = subprocess.run(
        [str(py), "-c", snippet],
        cwd=str(root),
        capture_output=True,
        text=True,
        timeout=120,
    )
    out = ((proc.stdout or "") + (proc.stderr or "")).strip()
    return proc.returncode, out


def _platform_running(name: str) -> bool:
    root = bejcapital_root()
    py = _bejcapital_python()
    snippet = f"""
import sys, json
sys.path.insert(0, {str(root)!r})
from app.agency.registry import get_platform_registry
from app.agency.platform_runner import is_platform_entry_running
reg = get_platform_registry()
entry = reg.get({name!r})
if not entry:
    print(json.dumps({{"running": False}}))
else:
    print(json.dumps({{"running": is_platform_entry_running(entry)}}))
"""
    try:
        proc = subprocess.run(
            [str(py), "-c", snippet],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=30,
        )
        if proc.returncode != 0:
            return False
        data = json.loads(proc.stdout.strip() or "{}")
        return bool(data.get("running"))
    except Exception:
        return False


def _port_open(host: str, port: int, timeout: float = 0.5) -> bool:
    import socket

    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def status_one(name: str) -> bool:
    if name == "hermes-dashboard":
        port = dashboard_port()
        if _pid_alive(run_dir() / "hermes-dashboard.pid"):
            return True
        # Socket probe only — HTTP /api/status from the dashboard worker deadlocks.
        return _port_open("127.0.0.1", port)
    if name in ("pimono", "pimono-proxy"):
        if oracle_llm_on_mac():
            return _health("http://127.0.0.1:5102/health")
        if name == "pimono":
            return _health("http://127.0.0.1:3099/health")
        return _health("http://127.0.0.1:5102/health")
    if name == "camofox-browser":
        port = camofox_port()
        return _health(f"http://127.0.0.1:{port}/health")
    if name == "bejmind":
        return _health("http://127.0.0.1:5002/ready")
    if name == "bejtrader":
        return _health("http://127.0.0.1:5001/health") or _platform_running("bejtrader")
    if name == "predictx":
        return _health("http://127.0.0.1:5004/health") or _platform_running("predictx")
    if name == "nautilus":
        return _health("http://127.0.0.1:5011/health") or _platform_running("nautilus")
    if name == "hermes-gateway":
        if _pid_alive(run_dir() / "gateway-manual.pid"):
            return True
        hermes = hermes_agent_root() / "venv" / "bin" / "hermes"
        if hermes.is_file():
            try:
                proc = subprocess.run(
                    [str(hermes), "gateway", "status"],
                    capture_output=True,
                    text=True,
                    timeout=3,
                )
                return proc.returncode == 0 and "PID" in (proc.stdout or "")
            except (subprocess.TimeoutExpired, OSError):
                return False
        return False
    if name == "agency":
        return _health(agency_health_url())
    if name == "cloudflared":
        if _pid_alive(run_dir() / "cloudflared-webhook.pid"):
            return True
        try:
            proc = subprocess.run(
                ["pgrep", "-f", "cloudflared tunnel --url"],
                capture_output=True,
                text=True,
                timeout=3,
            )
            return proc.returncode == 0 and bool((proc.stdout or "").strip())
        except (subprocess.TimeoutExpired, OSError):
            return False
    if name in INFRA_SERVICES:
        code, out = _infra_mgr("check", name)
        if code != 0:
            return False
        try:
            return bool(json.loads(out).get("running"))
        except json.JSONDecodeError:
            return False
    return False


def start_one(name: str) -> tuple[int, str]:
    if name == "hermes-dashboard":
        port = dashboard_port()
        pid_file = run_dir() / "hermes-dashboard.pid"
        if _pid_alive(pid_file) and status_one("hermes-dashboard"):
            return 0, f"hermes-dashboard already running on :{port}"
        hermes = hermes_agent_root() / "venv" / "bin" / "hermes"
        if not hermes.is_file():
            return 1, f"Missing {hermes}"
        log = log_dir() / "hermes-dashboard.log"
        env = os.environ.copy()
        env["HERMES_DASHBOARD_PORT"] = str(port)
        with open(log, "a", encoding="utf-8") as lf:
            proc = subprocess.Popen(
                [
                    str(hermes),
                    "dashboard",
                    "--port",
                    str(port),
                    "--no-open",
                    "--skip-build",
                ],
                stdout=lf,
                stderr=subprocess.STDOUT,
                cwd=str(hermes_agent_root()),
                env=env,
                start_new_session=True,
            )
        pid_file.write_text(str(proc.pid))
        time.sleep(2)
        if status_one("hermes-dashboard"):
            return 0, f"hermes-dashboard started http://127.0.0.1:{port}/ (pid {proc.pid})"
        return 1, f"hermes-dashboard failed to bind :{port} (see {log})"
    if name == "camofox-browser":
        script = bejcapital_root() / "app" / "scripts" / "start-camofox.sh"
        if not script.is_file():
            return 1, f"Missing {script}"
        env = {
            **os.environ,
            "CAMOFOX_ROOT": str(camofox_root()),
            "CAMOFOX_PORT": str(camofox_port()),
        }
        proc = subprocess.run(
            ["bash", str(script)],
            capture_output=True,
            text=True,
            timeout=600,
            env=env,
            cwd=str(bejcapital_root()),
        )
        out = ((proc.stdout or "") + (proc.stderr or "")).strip()
        if proc.returncode == 0 and status_one("camofox-browser"):
            return 0, out or f"camofox-browser started on :{camofox_port()}"
        return proc.returncode or 1, out or "camofox-browser failed to start"
    if name == "pimono" or name == "pimono-proxy":
        if oracle_llm_on_mac():
            script = (
                bejcapital_root()
                / "app"
                / "scripts"
                / "oracle"
                / "oracle-llm-tunnel.sh"
            )
            if not script.is_file():
                return 1, f"Missing {script}"
            proc = subprocess.run(
                ["bash", str(script), "start"],
                capture_output=True,
                text=True,
                timeout=120,
            )
            out = ((proc.stdout or "") + (proc.stderr or "")).strip()
            if proc.returncode == 0 and status_one("pimono-proxy"):
                return 0, out or "oracle LLM tunnel up (VM Pimono → Mac :5102)"
            return proc.returncode or 1, out or "oracle LLM tunnel failed"
        script = bejcapital_root() / "bejmind" / "scripts" / "start_pimono_stack.sh"
        if not script.is_file():
            return 1, f"Missing {script}"
        proc = subprocess.run(["bash", str(script)], capture_output=True, text=True, timeout=180)
        out = ((proc.stdout or "") + (proc.stderr or "")).strip()
        return proc.returncode, out or "pimono stack started"
    if name == "hermes-gateway":
        pid_file = run_dir() / "gateway-manual.pid"
        if _pid_alive(pid_file):
            return 0, "hermes-gateway already running"
        py = hermes_agent_root() / "venv" / "bin" / "python"
        log = log_dir() / "gateway-manual.log"
        with open(log, "a", encoding="utf-8") as lf:
            proc = subprocess.Popen(
                [str(py), "-m", "hermes_cli.main", "gateway", "run", "--replace"],
                stdout=lf,
                stderr=subprocess.STDOUT,
                cwd=str(hermes_agent_root()),
                start_new_session=True,
            )
        pid_file.write_text(str(proc.pid))
        time.sleep(2)
        return 0, f"hermes-gateway started (pid {proc.pid})"
    if name == "agency":
        port = agency_api_port()
        env = os.environ.copy()
        env["AGENCY_PORT"] = str(port)
        main_sh = bejcapital_root() / "main"
        if not main_sh.is_file():
            return 1, f"Missing {main_sh}"
        proc = subprocess.run(
            ["bash", str(main_sh), "start", "agency", "--no-foreground", "--no-reload"],
            cwd=str(bejcapital_root()),
            capture_output=True,
            text=True,
            timeout=180,
            env=env,
        )
        out = ((proc.stdout or "") + (proc.stderr or "")).strip()
        if proc.returncode == 0 and status_one("agency"):
            return 0, out or f"agency API started on :{port}"
        return proc.returncode, out or f"agency failed on :{port}"
    if name == "cloudflared":
        script = bejcapital_root() / "app" / "scripts" / "oracle" / "start-cloudflared-webhook.sh"
        if not script.is_file():
            return 1, f"Missing {script}"
        proc = subprocess.run(["bash", str(script)], capture_output=True, text=True, timeout=120)
        out = ((proc.stdout or "") + (proc.stderr or "")).strip()
        if proc.returncode == 0 and status_one("cloudflared"):
            return 0, out or "cloudflared webhook tunnel started"
        return proc.returncode or 1, out or "cloudflared failed"
    if name == "nginx":
        code, msg = _infra_mgr("start", name)
        if code == 0:
            port = dashboard_port()
            reload = bejcapital_root() / "app" / "scripts" / "nginx-reload-agency.sh"
            if reload.is_file():
                env = {
                    **os.environ,
                    "AGENCY_PORT": str(port),
                    "AGENCY_URL": f"http://127.0.0.1:{port}/api/status",
                }
                subprocess.run(
                    ["bash", str(reload)],
                    cwd=str(bejcapital_root()),
                    env=env,
                    capture_output=True,
                    timeout=90,
                )
        return code, msg
    if name in INFRA_SERVICES:
        return _infra_mgr("start", name)
    if name in PLATFORM_SERVICES:
        code, out = _run_in_bejcapital(
            ["start", name, "--no-foreground", "--background", "--no-reload"]
        )
        return code, out or f"started {name}"
    return 1, f"unknown service: {name}"


def stop_one(name: str) -> tuple[int, str]:
    if name == "hermes-dashboard":
        pid_file = run_dir() / "hermes-dashboard.pid"
        if _pid_alive(pid_file):
            try:
                pid = int(pid_file.read_text().strip())
                os.kill(pid, 15)
            except (ValueError, OSError):
                pass
        pid_file.unlink(missing_ok=True)
        hermes = hermes_agent_root() / "venv" / "bin" / "hermes"
        if hermes.is_file():
            subprocess.run([str(hermes), "dashboard", "--stop"], capture_output=True, timeout=30)
        return 0, "hermes-dashboard stopped"
    if name == "camofox-browser":
        script = bejcapital_root() / "app" / "scripts" / "stop-camofox.sh"
        if script.is_file():
            proc = subprocess.run(
                ["bash", str(script)],
                capture_output=True,
                text=True,
                timeout=120,
                env={**os.environ, "CAMOFOX_ROOT": str(camofox_root())},
            )
            out = ((proc.stdout or "") + (proc.stderr or "")).strip()
            return proc.returncode, out or "camofox-browser stopped"
        return 0, "camofox-browser stop script missing"
    if name in ("pimono", "pimono-proxy"):
        if oracle_llm_on_mac():
            script = (
                bejcapital_root()
                / "app"
                / "scripts"
                / "oracle"
                / "oracle-llm-tunnel.sh"
            )
            if script.is_file():
                subprocess.run(["bash", str(script), "stop"], capture_output=True, timeout=60)
            return 0, "oracle LLM tunnel stopped"
        script = bejcapital_root() / "bejmind" / "scripts" / "stop_pimono_stack.sh"
        if script.is_file():
            subprocess.run(["bash", str(script)], capture_output=True, timeout=120)
        return 0, "pimono stack stopped"
    if name == "hermes-gateway":
        pid_file = run_dir() / "gateway-manual.pid"
        if _pid_alive(pid_file):
            try:
                os.kill(int(pid_file.read_text().strip()), 15)
            except (ValueError, OSError):
                pass
        pid_file.unlink(missing_ok=True)
        hermes = hermes_agent_root() / "venv" / "bin" / "hermes"
        if hermes.is_file():
            subprocess.run([str(hermes), "gateway", "stop"], capture_output=True, timeout=30)
        return 0, "hermes-gateway stopped"
    if name == "cloudflared":
        pid_file = run_dir() / "cloudflared-webhook.pid"
        if _pid_alive(pid_file):
            try:
                os.kill(int(pid_file.read_text().strip()), 15)
            except (ValueError, OSError):
                pass
        pid_file.unlink(missing_ok=True)
        subprocess.run(
            ["pkill", "-TERM", "-f", "cloudflared tunnel --url"],
            capture_output=True,
            timeout=10,
        )
        return 0, "cloudflared webhook tunnel stopped"
    if name == "agency":
        code, out = _run_in_bejcapital(["stop", "agency"])
        return code, out or "agency stopped"
    if name in INFRA_SERVICES:
        return _infra_mgr("stop", name)
    if name in PLATFORM_SERVICES:
        code, out = _run_in_bejcapital(["stop", name])
        return code, out or f"stopped {name}"
    return 1, f"unknown service: {name}"


def toggle_one(name: str) -> tuple[int, str]:
    if status_one(name):
        return stop_one(name)
    return start_one(name)


def _status_one_safe(name: str) -> bool:
    try:
        return status_one(name)
    except Exception:
        return False


def status_json() -> dict[str, Any]:
    from concurrent.futures import ThreadPoolExecutor, as_completed

    services: dict[str, bool] = {}
    order = service_order()
    with ThreadPoolExecutor(max_workers=min(8, len(order))) as pool:
        futures = {pool.submit(_status_one_safe, name): name for name in order}
        for fut in as_completed(futures):
            name = futures[fut]
            try:
                services[name] = bool(fut.result())
            except Exception:
                services[name] = False
    return {
        "services": services,
        "available": True,
        "dashboard_port": dashboard_port(),
        "deploy_profile": deploy_profile(),
        "service_order": order,
    }


def start_llm() -> tuple[int, str]:
    return start_one("pimono")


def start_all() -> tuple[int, str]:
    messages: list[str] = []
    if deploy_profile() == "cloud":
        order = [
            "ollama",
            "camofox-browser",
            "agency",
            "pimono",
            "pimono-proxy",
            "bejmind",
            "bejtrader",
            "nautilus",
            "predictx",
            "hermes-dashboard",
            "hermes-gateway",
            "cloudflared",
        ]
    else:
        order = [
            "nginx",
            "ollama",
            "camofox-browser",
            "agency",
            "pimono",
            "pimono-proxy",
            "bejmind",
            "bejtrader",
            "nautilus",
            "predictx",
            "hermes-dashboard",
            "hermes-gateway",
            "ngrok",
        ]
    code = 0
    for name in order:
        c, msg = start_one(name)
        if msg:
            messages.append(f"{name}: {msg}")
        if c != 0:
            code = c
    return code, "\n".join(messages)


def stop_all() -> tuple[int, str]:
    messages: list[str] = []
    order = list(reversed(service_order()))
    code = 0
    for name in order:
        c, msg = stop_one(name)
        if msg:
            messages.append(f"{name}: {msg}")
        if c != 0:
            code = c
    return code, "\n".join(messages)


def main(argv: Optional[list[str]] = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    cmd = args[0] if args else "status"
    svc = args[1] if len(args) > 1 else ""

    if cmd == "status":
        for name in service_order():
            state = "up" if status_one(name) else "down"
            print(f"{name}: {state}")
        return 0
    if cmd == "status-json":
        print(json.dumps(status_json()))
        return 0
    if cmd == "start-llm":
        code, msg = start_llm()
        if msg:
            print(msg)
        return code
    if cmd == "start-all":
        code, msg = start_all()
        if msg:
            print(msg)
        return code
    if cmd == "stop-all":
        code, msg = stop_all()
        if msg:
            print(msg)
        return code
    if cmd == "start" and svc:
        code, msg = start_one(svc)
        if msg:
            print(msg)
        return code
    if cmd == "stop" and svc:
        code, msg = stop_one(svc)
        if msg:
            print(msg)
        return code
    if cmd == "toggle" and svc:
        code, msg = toggle_one(svc)
        if msg:
            print(msg)
        return code
    print(
        "Usage: bejcapital_fleet <status|status-json|start|stop|toggle|start-llm|start-all|stop-all> [service]",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
