"""Base tool contract.

Every tool in AI-News-Agent inherits from BaseTool. This enforces a uniform
interface for discovery, execution, cost estimation, and health reporting.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


def _load_dotenv() -> None:
    """Load .env into os.environ once at import time."""
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if value[:1] in ("'", '"'):
            quote = value[0]
            end = value.find(quote, 1)
            value = value[1:end] if end != -1 else value[1:]
        if key and key not in os.environ:
            os.environ[key] = value


_load_dotenv()


class ToolTier(str, Enum):
    CORE = "core"
    VOICE = "voice"
    GENERATE = "generate"
    SOURCE = "source"
    ANALYZE = "analyze"
    PUBLISH = "publish"


class ToolStability(str, Enum):
    EXPERIMENTAL = "experimental"
    BETA = "beta"
    PRODUCTION = "production"


class ToolStatus(str, Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    DEGRADED = "degraded"


class ToolRuntime(str, Enum):
    LOCAL = "local"
    LOCAL_GPU = "local_gpu"
    API = "api"
    HYBRID = "hybrid"


@dataclass
class ToolContract:
    """What a tool declares - the registry groups by capability/provider."""

    name: str
    capability: str
    provider: str
    description: str
    tier: ToolTier = ToolTier.CORE
    stability: ToolStability = ToolStability.PRODUCTION
    runtime: ToolRuntime = ToolRuntime.LOCAL
    status: ToolStatus = ToolStatus.AVAILABLE
    cost_per_call_usd: float = 0.0
    dependencies: list[str] = field(default_factory=list)
    agent_skills: list[str] = field(default_factory=list)
    input_schema: dict[str, Any] = field(default_factory=dict)
    output_schema: dict[str, Any] = field(default_factory=dict)


class BaseTool:
    """Base class implementing the expanded ToolContract."""

    name: str = "base"
    capability: str = "base"
    provider: str = "base"
    description: str = "Base tool."
    tier: ToolTier = ToolTier.CORE
    stability: ToolStability = ToolStability.PRODUCTION
    runtime: ToolRuntime = ToolRuntime.LOCAL
    cost_per_call_usd: float = 0.0
    dependencies: list[str] = []
    agent_skills: list[str] = []
    input_schema: dict[str, Any] = {}
    output_schema: dict[str, Any] = {}

    # ------------------------------------------------------------------ #
    def contract(self) -> ToolContract:
        h = self.health()
        try:
            status = ToolStatus(h.get("status", "unavailable"))
        except ValueError:
            status = ToolStatus.UNAVAILABLE
        return ToolContract(
            name=self.name,
            capability=self.capability,
            provider=self.provider,
            description=self.description,
            tier=self.tier if isinstance(self.tier, ToolTier) else ToolTier.CORE,
            stability=self.stability if isinstance(self.stability, ToolStability) else ToolStability.PRODUCTION,
            runtime=self.runtime if isinstance(self.runtime, ToolRuntime) else ToolRuntime.LOCAL,
            status=status,
            cost_per_call_usd=self.cost_per_call_usd,
            dependencies=list(self.dependencies),
            agent_skills=list(self.agent_skills),
            input_schema=dict(self.input_schema),
            output_schema=dict(self.output_schema),
        )

    def health(self) -> dict[str, Any]:
        """Report availability. Default: check every declared dependency."""
        missing = [d for d in self.dependencies if shutil.which(d) is None]
        status = ToolStatus.AVAILABLE if not missing else ToolStatus.UNAVAILABLE
        return {"status": status, "missing_dependencies": missing}

    def support_envelope(self) -> dict[str, Any]:
        c = self.contract()
        return {
            "name": c.name,
            "capability": c.capability,
            "provider": c.provider,
            "tier": c.tier.value,
            "stability": c.stability.value,
            "runtime": c.runtime.value,
            "status": c.status.value,
            "cost_per_call_usd": c.cost_per_call_usd,
            "dependencies": c.dependencies,
            "agent_skills": c.agent_skills,
        }

    def execute(self, **kwargs: Any) -> dict[str, Any]:  # pragma: no cover
        raise NotImplementedError(f"{self.__class__.__name__}.execute() not implemented")

    def estimate_cost(self, **kwargs: Any) -> float:
        return float(self.cost_per_call_usd)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<{self.__class__.__name__} name={self.name!r} capability={self.capability!r}>"


def run(cmd: list[str], *, timeout: int = 600, cwd: str | None = None,
        env: dict[str, str] | None = None) -> dict[str, Any]:
    """Run a subprocess and return a structured result."""
    try:
        proc = subprocess.run(
            cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout,
        )
        return {
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "cmd": " ".join(cmd),
        }
    except FileNotFoundError:
        return {"ok": False, "returncode": -1, "stdout": "", "stderr": f"command not found: {cmd[0]}", "cmd": " ".join(cmd)}
    except subprocess.TimeoutExpired:
        return {"ok": False, "returncode": -1, "stdout": "", "stderr": "timeout", "cmd": " ".join(cmd)}