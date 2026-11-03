"""Tool registry with status, stability, and support-envelope reporting.

The registry discovers all registered tools, reports their availability, and
lets the orchestrator/agents query capabilities by tier, status, etc.
"""

from __future__ import annotations

import importlib
import inspect
import json
from pathlib import Path
from typing import Any

from tools.base_tool import BaseTool, ToolStatus, ToolTier, ToolRuntime


class ToolRegistry:
    """Central registry of all AI-News-Agent tools."""

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        if not tool.name:
            raise ValueError("Tool must have a non-empty name")
        self._tools[tool.name] = tool

    def clear(self) -> None:
        self._tools.clear()

    def register_module(self, module) -> list[str]:
        registered: list[str] = []
        for _, cls in inspect.getmembers(module, inspect.isclass):
            if cls is BaseTool or not issubclass(cls, BaseTool):
                continue
            if cls.__module__ != module.__name__ or inspect.isabstract(cls):
                continue
            try:
                tool = cls()
            except Exception:
                continue
            self.register(tool)
            registered.append(tool.name)
        return registered

    def discover(self) -> list[str]:
        """Auto-discover every tool in tools/."""
        self.clear()
        pkg = importlib.import_module("tools")
        pkg_dir = Path(pkg.__file__).resolve().parent
        names: list[str] = []
        for p in sorted(pkg_dir.glob("*.py")):
            if p.name.startswith("_") or p.name in ("base_tool.py", "tool_registry.py"):
                continue
            mod_name = f"tools.{p.stem}"
            try:
                mod = importlib.import_module(mod_name)
            except Exception:
                continue
            names.extend(self.register_module(mod))
        return names

    def get(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def all_tools(self) -> list[BaseTool]:
        return list(self._tools.values())

    def by_capability(self, capability: str) -> list[BaseTool]:
        return [t for t in self._tools.values() if t.capability == capability]

    def by_tier(self, tier: ToolTier) -> list[BaseTool]:
        return [t for t in self._tools.values() if t.tier == tier]

    def available(self) -> list[BaseTool]:
        return [t for t in self._tools.values() if t.health()["status"] == ToolStatus.AVAILABLE.value]

    def support_envelope(self) -> dict[str, Any]:
        return {t.name: t.support_envelope() for t in self._tools.values()}

    def capability_catalog(self) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for cap in sorted({t.capability for t in self._tools.values()}):
            out[cap] = [t.name for t in self._tools.values() if t.capability == cap]
        return out

    def provider_menu(self) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for t in self._tools.values():
            out.setdefault(t.capability, []).append({
                "provider": t.provider,
                "tool": t.name,
                "status": t.health()["status"],
                "cost_per_call_usd": t.cost_per_call_usd,
            })
        return out

    def summary(self) -> str:
        lines = [f"AI-News-Agent tool registry: {len(self._tools)} tools", ""]
        for cap, tools in sorted(self.capability_catalog().items()):
            lines.append(f"{cap}:")
            for name in tools:
                t = self._tools[name]
                h = t.health()
                lines.append(f"  - {name} ({t.provider}) [{h['status']}] ${t.cost_per_call_usd}")
        return "\n".join(lines)


registry = ToolRegistry()


def main() -> int:
    registry.discover()
    print(registry.summary())
    print("\nCapability catalog:")
    print(json.dumps(registry.capability_catalog(), indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
